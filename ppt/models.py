from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q, Sum
from django.template.defaultfilters import date, slugify
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, gettext
from django.core.exceptions import ValidationError
from markdown import markdown
from textile import textile

from dm_apps.utils import custom_send_mail
from lib.functions.custom_functions import fiscal_year, listrify, nz
from lib.templatetags.custom_filters import percentage
from ppt import emails
from ppt.utils import get_risk_rating
from shared_models import models as shared_models
# Choices for language
from shared_models.models import SimpleLookup, Lookup, HelpTextLookup, MetadataFields, Region
from shared_models.utils import get_metadata_string
from inventory import models as inventory_models


YES_NO_CHOICES = (
    (True, gettext("Yes")),
    (False, gettext("No")),
)

# This factor is how many OM dollars 1 dollar of salary is worth.  So Total (in OM) = OM + SALARY * FACTOR
SALARY_TO_OM_FACTOR = 1.27


class PPTAdminUser(models.Model):
    mode_choices = (
        (1, "read"),
        (2, "edit"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="ppt_admin_user", verbose_name=_("DM Apps user"))
    region = models.ForeignKey(Region, verbose_name=_("regional administrator?"), related_name="projects_admin_user", on_delete=models.CASCADE, blank=True,
                               null=True)
    is_national_admin = models.BooleanField(default=False, verbose_name=_("national administrator?"), choices=YES_NO_CHOICES)

    # admin users can toggle helptext edit mode on and off
    mode = models.IntegerField(choices=mode_choices, default=1)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        ordering = ["-is_national_admin", "region", "user__first_name", ]


class CSRFTheme(SimpleLookup):
    code = models.CharField(max_length=25)

    def __str__(self):
        return f"{self.code}: {self.tname}"


class CSRFSubTheme(SimpleLookup):
    name = models.CharField(max_length=1000, verbose_name=_("name (en)"))
    csrf_theme = models.ForeignKey(CSRFTheme, on_delete=models.DO_NOTHING, related_name="sub_themes", verbose_name=_("CSRF theme"))


class CSRFPriority(SimpleLookup):
    csrf_sub_theme = models.ForeignKey(CSRFSubTheme, on_delete=models.DO_NOTHING, related_name="priorities", verbose_name=_("CSRF sub-theme"))
    code = models.CharField(verbose_name=_("Priority identification number"), max_length=25, unique=True)
    name = models.CharField(max_length=1000, verbose_name=_("priority for research (en)"))
    nom = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("priority for research (fr)"))

    class Meta:
        ordering = ['code', "name"]

    def __str__(self):
        return mark_safe(f'{self.code}: {self.tname}')


class CSRFClientInformation(Lookup):
    csrf_priority = models.ForeignKey(CSRFPriority, on_delete=models.DO_NOTHING, related_name="client_information", verbose_name=_("CSRF priority"))
    name = models.CharField(max_length=1000, verbose_name=_("name (en)"), blank=True, null=True, editable=False)
    nom = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("name (fr)"), editable=False)
    description_en = models.TextField(verbose_name=_("additional client information (en)"))
    description_fr = models.TextField(blank=True, null=True, verbose_name=_("additional client information (fr)"))
    fiscal_year = models.ForeignKey(shared_models.FiscalYear, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("fiscal year"))

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.quickname_en
        if not self.nom and self.description_fr:
            self.nom = self.quickname_fr
        super().save(*args, **kwargs)

    @property
    def quickname_en(self):
        first_part = self.description_en.split("\n")[0]
        first_part = first_part.replace(":", "")
        if len(first_part) > 90:
            first_part = first_part[:90]
        return mark_safe(f'{self.csrf_priority.code} &rarr; {first_part}...')

    @property
    def quickname_fr(self):
        first_part = self.description_fr.split("\n")[0]
        first_part = first_part.replace(":", "")
        if len(first_part) > 90:
            first_part = first_part[:90]
        return mark_safe(f'{self.csrf_priority.code} &rarr; {first_part}...')

    class Meta:
        ordering = ['csrf_priority__code', "name"]

    def __str__(self):
        return mark_safe(self.tname)


class Theme(SimpleLookup):
    pass


class UpcomingDate(models.Model):
    region = models.ForeignKey(shared_models.Region, on_delete=models.DO_NOTHING, related_name="project_upcoming_dates2",
                               verbose_name=_("region"))
    description_en = models.TextField(verbose_name=_("description (en)"))
    description_fr = models.TextField(blank=True, null=True, verbose_name=_("description (fr)"))
    date = models.DateTimeField()
    is_deadline = models.BooleanField(default=False)

    class Meta:
        ordering = ["-date", ]

    @property
    def tdescription(self):
        # check to see if a french value is given
        if getattr(self, str(_("description_en"))):
            my_str = "{}".format(getattr(self, str(_("description_en"))))
        # if there is no translated term, just pull from the english field
        else:
            my_str = self.description_en
        return my_str


class FunctionalGroup(SimpleLookup):
    sections = models.ManyToManyField(shared_models.Section, related_name="functional_groups2", blank=True)
    theme = models.ForeignKey(Theme, on_delete=models.DO_NOTHING, related_name="functional_groups", blank=True, null=True)


class ActivityType(SimpleLookup):
    class Meta:
        ordering = ['id', ]


class FundingSource(SimpleLookup):
    funding_source_type_choices = (
        (1, _("A-base")),
        (2, _("B-base")),
        (3, _("C-base")),
    )
    funding_source_type_colors = (
        (1, "#a7aef9"),
        (2, "#d9a7f9"),
        (3, "#eff9a7"),
    )
    name = models.CharField(max_length=255)
    funding_source_type = models.IntegerField(choices=funding_source_type_choices)
    is_competitive = models.BooleanField(default=False, verbose_name=_("is competitive funding?"))

    def __str__(self):
        return f"{self.tname} ({self.get_funding_source_type_display()})"

    @property
    def display2(self):
        return f"{self.get_funding_source_type_display()} - {self.tname}"

    @property
    def display3(self):
        mystr = f"{self.get_funding_source_type_display()} - {self.tname}"
        if self.is_competitive:
            mystr += " ({})".format(_("competitive"))
        return mystr

    class Meta:
        ordering = ['funding_source_type', 'name', ]
        unique_together = [('funding_source_type', 'name'), ]


class ActivityClassification(SimpleLookup):
    pass


class Tag(SimpleLookup):
    pass


class HelpText(HelpTextLookup):
    model = models.CharField(max_length=255, blank=True, null=True)


class Service(SimpleLookup):
    coordinator = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("service coordinator"), related_name="services")
    regions = models.ManyToManyField(shared_models.Region, related_name="services", blank=True, verbose_name=_("For which regions"))

    def __str__(self):
        mystr = self.tname
        if self.regions.exists():
            mystr += f" ({listrify(self.regions.all())})"
        return mystr


class Project(models.Model):
    # basic
    section = models.ForeignKey(shared_models.Section, on_delete=models.DO_NOTHING, null=True, related_name="ppt", verbose_name=_("section"))
    title = models.TextField(verbose_name=_("Project title"))
    activity_type = models.ForeignKey(ActivityType, on_delete=models.DO_NOTHING, blank=False, null=True, verbose_name=_("activity type"))
    functional_group = models.ForeignKey(FunctionalGroup, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="projects",
                                         verbose_name=_("Functional group"))
    default_funding_source = models.ForeignKey(FundingSource, on_delete=models.DO_NOTHING, blank=False, null=True, related_name="projects",
                                               verbose_name=_("primary funding source"))
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_("Tags / keywords"), related_name="projects")
    references = models.ManyToManyField(shared_models.Citation, blank=True, verbose_name=_("references"), related_name="projects", editable=False)

    # HTML field
    overview = models.TextField(blank=True, null=True, verbose_name=_("Project overview"))

    is_hidden = models.BooleanField(default=False, verbose_name=_("Should the project be hidden from other users?"))

    # ACRDP fields
    organization = models.ForeignKey(shared_models.Organization, on_delete=models.DO_NOTHING, related_name="projects",
                                     verbose_name=_("physical location (ACRDP)"), blank=True, null=True)
    species_involved = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("species involved (ACRDP)"))
    team_description = models.TextField(blank=True, null=True, verbose_name=_("description of team and required qualifications (ACRDP)"))
    rationale = models.TextField(blank=True, null=True, verbose_name=_("project problem / rationale (ACRDP)"))
    experimental_protocol = models.TextField(blank=True, null=True, verbose_name=_("experimental protocol (ACRDP)"))

    # CSRF fields
    csrf_fiscal_year = models.ForeignKey(shared_models.FiscalYear, on_delete=models.DO_NOTHING, blank=True, null=True,
                                         verbose_name=_("CSRF application fiscal year (CSRF)"),  related_name="csrf_projects")

    client_information = models.ForeignKey(CSRFClientInformation, on_delete=models.DO_NOTHING, blank=True, null=True,
                                           verbose_name=_("Specific Client Question (CSRF)"), related_name="projects")
    second_priority = models.ForeignKey(CSRFPriority, on_delete=models.DO_NOTHING, blank=True, null=True,
                                        verbose_name=_("Linkage to second priority (CSRF)"), related_name="projects")

    objectives = models.TextField(blank=True, null=True, verbose_name=_("project objectives (CSRF)"))
    innovation = models.TextField(blank=True, null=True, verbose_name=_("innovation (CSRF)"))
    other_funding = models.TextField(blank=True, null=True, verbose_name=_("other sources of funding (CSRF)"))  # SARA

    # SARA Fields
    reporting_mechanism = models.TextField(blank=True, null=True, verbose_name=_("quarterly reporting mechanisms (SARA)"))  # SARA
    future_funding_needs = models.TextField(blank=True, null=True, verbose_name=_("description of future funding needs, if any (SARA)"))  # SARA

    # DMA - link to inventory app
    dmas = models.ManyToManyField(inventory_models.DMA, blank=True, verbose_name=_("Data management agreements (linked to Science Data Inventory)"))



    # calculated fields
    start_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Start date of project"), editable=False)
    end_date = models.DateTimeField(blank=True, null=True, verbose_name=_("End date of project"), editable=False)
    funding_sources = models.ManyToManyField(FundingSource, editable=False, verbose_name=_("complete list of funding sources"))
    staff_search_field = models.CharField(editable=False, max_length=5000, blank=True, null=True)
    lead_staff = models.ManyToManyField("Staff", editable=False, verbose_name=_("project leads"))
    fiscal_years = models.ManyToManyField(shared_models.FiscalYear, editable=False, verbose_name=_("fiscal years"))
    starting_fy = models.ForeignKey(shared_models.FiscalYear, on_delete=models.DO_NOTHING, editable=False, blank=True, null=True,
                                    verbose_name=_("starting fiscal year"), related_name="project_starting_years")
    # metadata
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="last_mod_by_projects_project", blank=True, null=True)

    def save(self, *args, **kwargs):
        project_years = self.years.order_by("fiscal_year")  # being explicit about ordering here is impnt

        if project_years.exists():
            self.starting_fy = project_years.first().fiscal_year

        # list of things to do if there are project years
        if project_years.exists():
            # set the start and end dates based on project years
            self.start_date = self.years.first().start_date
            self.end_date = self.years.last().end_date

            # reset some calculated fields
            self.staff_search_field = ""
            self.funding_sources.clear()
            self.lead_staff.clear()

            for y in project_years:

                # search for and staff and concatenate into a search field
                for s in y.staff_set.all():
                    if s.smart_name:
                        self.staff_search_field += s.smart_name + " "
                    if s.is_lead and not self.lead_staff.filter(user=s.user).exists():
                        self.lead_staff.add(s)

                # cycle through all costs and pull out funding sources
                for c in y.costs:
                    self.funding_sources.add(c.funding_source)

                if y.fiscal_year:
                    self.fiscal_years.add(y.fiscal_year)

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.project_id_name

    @property
    def project_id_name(self):
        return _("Project") + f" {self.id}"

    @property
    def metadata(self):
        return get_metadata_string(self.created_at, None, self.updated_at, self.modified_by)

    @property
    def dates(self):
        my_str = date(self.start_date)
        if self.end_date:
            my_str += f" &rarr; {date(self.end_date)}"
        return mark_safe(my_str)

    @property
    def has_unsubmitted_years(self):
        return self.years.filter(submitted__isnull=True).exists()

    @property
    def region(self):
        if self.section:
            return self.division.branch.sector.region

    @property
    def division(self):
        return self.section.division

    @property
    def overview_html(self):
        if self.overview:
            return mark_safe(markdown(self.overview))

    @property
    def objectives_html(self):
        if self.objectives:
            return mark_safe(markdown(self.objectives))

    @property
    def innovation_html(self):
        if self.innovation:
            return mark_safe(markdown(self.innovation))

    @property
    def other_funding_html(self):
        if self.other_funding:
            return mark_safe(markdown(self.other_funding))

    @property
    def team_description_html(self):
        if self.team_description:
            return mark_safe(markdown(self.team_description))

    @property
    def rationale_html(self):
        if self.rationale:
            return mark_safe(markdown(self.rationale))

    @property
    def experimental_protocol_html(self):
        if self.experimental_protocol:
            return mark_safe(markdown(self.experimental_protocol))

    @property
    def client_information_html(self):
        if self.client_information:
            return mark_safe(textile(self.client_information.tdescription))

    def get_funding_sources(self):
        # look through all expenses and allocations and compile a unique list of funding sources (for all years of project)
        my_dict = {}
        for year in self.years.all():
            for item in year.staff_set.all():
                if item.funding_source and item.amount and item.amount > 0:
                    my_dict[item.funding_source] = my_dict.get(item.funding_source, 0) + item.amount
            for item in year.omcost_set.all():
                if item.funding_source and item.amount and item.amount > 0:
                    my_dict[item.funding_source] = my_dict.get(item.funding_source, 0) + item.amount

            for item in year.capitalcost_set.all():
                if item.funding_source and item.amount and item.amount > 0:
                    my_dict[item.funding_source] = my_dict.get(item.funding_source, 0) + item.amount

            for item in year.salaryallocation_set.all():
                if item.funding_source and item.amount and item.amount > 0:
                    my_dict[item.funding_source] = my_dict.get(item.funding_source, 0) + item.amount

            for item in year.omallocation_set.all():
                if item.funding_source and item.amount and item.amount > 0:
                    my_dict[item.funding_source] = my_dict.get(item.funding_source, 0) + item.amount

            for item in year.capitalallocation_set.all():
                if item.funding_source and item.amount and item.amount > 0:
                    my_dict[item.funding_source] = my_dict.get(item.funding_source, 0) + item.amount

        sorted_list = sorted(my_dict.items(), key=lambda item: item[1], reverse=True)
        sorted_list = [tup[0] for tup in sorted_list]
        if self.default_funding_source not in sorted_list and self.default_funding_source is not None:
            sorted_list.append(self.default_funding_source)
        return sorted_list

    @property
    def is_acrdp(self):
        if self.default_funding_source and "acrdp" in self.default_funding_source.name.lower():
            return True

    @property
    def is_csrf(self):
        if self.default_funding_source and "csrf" in self.default_funding_source.name.lower():
            return True

    @property
    def is_sara(self):
        if self.default_funding_source and "sara" in self.default_funding_source.name.lower():
            return True

    @property
    def fiscal_years_display(self):
        if self.years.exists():

            return listrify([str(y) for y in self.years.all()])
        else:
            return "<em>{}</em>".format(_("This project has no fiscal years added yet."))

    def year_status(self, fiscal_year):
        if fiscal_year:
            py_qs = ProjectYear.objects.filter(fiscal_year_id=fiscal_year, project=self)
            if py_qs:
                return py_qs.get().get_status_display()
        return None


class ProjectYear(models.Model):
    status_choices = [
        (1, "Draft"),
        (2, "Submitted"),
        (3, "Reviewed"),
        (6, "Recommended"),
        (4, "Approved"),
        (5, "Not Approved"),
        (9, "Cancelled"),
    ]
    status = models.IntegerField(default=1, editable=False, choices=status_choices)

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="years", verbose_name=_("project"))
    start_date = models.DateTimeField(default=timezone.now, verbose_name=_("Start date for this year of the project"))
    end_date = models.DateTimeField(blank=True, null=True, verbose_name=_("End date for this year of the project"))

    # HTML field
    priorities = models.TextField(blank=True, null=True, verbose_name=_("year-specific priorities"))
    # HTML field
    deliverables = models.TextField(blank=True, null=True, verbose_name=_("deliverables / activities"), editable=False)
    services = models.ManyToManyField(Service, blank=True, verbose_name=_("Will any of the following services be required?"), related_name="years")

    # SPECIALIZED EQUIPMENT
    ########################
    requires_specialized_equipment = models.BooleanField(default=False, verbose_name=_(
        "Will the project require the purchase, design or fabrication of specialized laboratory or field equipment?"))
    technical_service_needs = models.TextField(blank=True, null=True, verbose_name=_("What technical services are being requested?"))
    mobilization_needs = models.TextField(blank=True, null=True, verbose_name=_(
        "Do you anticipate needing assistance with mobilization/demobilization of this equipment?"))

    # FIELD COMPONENT
    #################
    has_field_component = models.BooleanField(default=False, verbose_name=_("Does this project involved a field component?"))
    vehicle_needs = models.TextField(blank=True, null=True,
                                     verbose_name=_("Describe need for vehicle (type of vehicle, number of weeks, time-frame)"))
    has_ship_needs = models.BooleanField(default=False, verbose_name=_("Ship (Coast Guard, charter vessel) Requirements?"), choices=YES_NO_CHOICES)
    ship_needs = models.TextField(blank=True, null=True, verbose_name=_("Description of Ship (Coast Guard, charter vessel) Requirements"))
    coip_reference_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_(
        "If this project links to a ship time request in COIP, please include the COIP application number here."))
    instrumentation = models.TextField(blank=True, null=True,
                                       verbose_name=_("What field instrumentation will be deployed during this project?"))
    owner_of_instrumentation = models.TextField(blank=True, null=True, verbose_name=_(
        "Who is the owner/curator of this instrumentation, if known?"))
    # -- > Field staff
    requires_field_staff = models.BooleanField(default=False, verbose_name=_("Do you require field support staff?"))
    field_staff_needs = models.TextField(blank=True, null=True, verbose_name=_("If so, please include some additional detail, "
                                                                               "e.g., how many people are likely to be required and when"))

    # DATA COMPONENT
    ################
    has_data_component = models.BooleanField(default=False, verbose_name=_("Will new data be collected or generated?"))
    data_collected = models.TextField(blank=True, null=True, verbose_name=_("What type of data will be collected"))
    data_products = models.TextField(blank=True, null=True, verbose_name=_("What data products will be generated (e.g. models, indices)?"))
    open_data_eligible = models.BooleanField(default=False, verbose_name=_("Are these data / data products eligible "
                                                                           "to be placed on the Open Data Platform?"))
    data_storage_plan = models.TextField(blank=True, null=True, verbose_name=_("Data storage / archiving plan"))
    data_management_needs = models.TextField(blank=True, null=True, verbose_name=_("Describe what data management support is required, "
                                                                                   "if any."))

    # LAB COMPONENT
    ###############
    has_lab_component = models.BooleanField(default=False, verbose_name=_("Does this project involve laboratory work?"))

    # maritimes only - DELETE ME
    requires_abl_services = models.BooleanField(default=False, verbose_name=_(
        "Does this project require the services of Aquatic Biotechnology Lab (ABL)?"), editable=False)

    requires_lab_space = models.BooleanField(default=False, verbose_name=_("Is laboratory space required?"))
    requires_other_lab_support = models.BooleanField(default=False, verbose_name=_(
        "Does this project require other specialized laboratory support or services (provide details below)?"))
    other_lab_support_needs = models.TextField(blank=True, null=True, verbose_name=_(
        "Describe other laboratory requirements relevant for project planning purposes."))

    it_needs = models.TextField(blank=True, null=True, verbose_name=_("Special IT requirements (software, licenses, hardware)"))
    additional_notes = models.TextField(blank=True, null=True, verbose_name=_("additional notes"))

    # CODING
    ########
    # coding
    responsibility_center = models.ForeignKey(shared_models.ResponsibilityCenter, on_delete=models.DO_NOTHING, blank=True,
                                              null=True, related_name='projects_ppt',
                                              verbose_name=_("responsibility center (if known)"), editable=False)
    allotment_code = models.ForeignKey(shared_models.AllotmentCode, on_delete=models.DO_NOTHING, blank=True, null=True,
                                       related_name='projects_ppt', verbose_name=_("allotment code (if known)"), editable=False)
    existing_project_codes = models.ManyToManyField(shared_models.Project, blank=True, verbose_name=_("existing project codes (if known)"),
                                                    related_name="projects")

    # admin
    submitted = models.DateTimeField(editable=False, blank=True, null=True)
    administrative_notes = models.TextField(blank=True, null=True, verbose_name=_("administrative notes"))

    # metadata
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="last_mod_by_projects_projectyear", blank=True,
                                    null=True)

    # calculated
    fiscal_year = models.ForeignKey(shared_models.FiscalYear, on_delete=models.DO_NOTHING, editable=False, blank=True, null=True,
                                    verbose_name=_("fiscal year"))
    coding = models.TextField(blank=True, null=True, verbose_name=_("financial coding"), editable=False)

    def update_modified_by(self, user):
        self.modified_by = user
        self.save()

    @property
    def metadata(self):
        return get_metadata_string(self.created_at, None, self.updated_at, self.modified_by)

    class Meta:
        ordering = ["project", "fiscal_year"]
        unique_together = ["project", "fiscal_year"]

    def save(self, *args, **kwargs):
        # get the fiscal year based on the start date
        if self.start_date:
            self.fiscal_year_id = fiscal_year(self.start_date, sap_style=True)
        # save the project whenever a project year is saved
        self.coding = self.get_coding()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.fiscal_year) if self.fiscal_year else gettext("NEW PROJECT YEAR")

    @property
    def costs(self):
        om_qry = self.omcost_set
        capital_qry = self.capitalcost_set
        staff_qry = self.staff_set
        my_list = []
        if om_qry.exists():
            my_list.extend([c for c in om_qry.all()])
        if capital_qry.exists():
            my_list.extend([c for c in capital_qry.all()])
        if staff_qry.exists():
            my_list.extend([c for c in staff_qry.all()])
        return my_list

    @property
    def allocations(self):
        om_qry = self.omallocation_set
        capital_qry = self.capitalallocation_set
        staff_qry = self.salaryallocation_set
        my_list = []
        if om_qry.exists():
            my_list.extend([c for c in om_qry.all()])
        if capital_qry.exists():
            my_list.extend([c for c in capital_qry.all()])
        if staff_qry.exists():
            my_list.extend([c for c in staff_qry.all()])
        return my_list

    @property
    def om_costs(self):
        return nz(self.omcost_set.aggregate(dsum=Sum("amount"))["dsum"], 0)

    @property
    def salary_costs(self):
        return nz(self.staff_set.aggregate(dsum=Sum("amount"))["dsum"], 0)

    @property
    def capital_costs(self):
        return nz(self.capitalcost_set.aggregate(dsum=Sum("amount"))["dsum"], 0)

    @property
    def om_allocations(self):
        return nz(self.omallocation_set.aggregate(dsum=Sum("amount"))["dsum"], 0)

    @property
    def salary_allocations(self):
        return nz(self.salaryallocation_set.aggregate(dsum=Sum("amount"))["dsum"], 0)

    @property
    def capital_allocations(self):
        return nz(self.capitalallocation_set.aggregate(dsum=Sum("amount"))["dsum"], 0)

    def add_all_om_costs(self):
        for obj in OMCategory.objects.all():
            if not self.omcost_set.filter(om_category=obj).exists():
                OMCost.objects.create(
                    project_year=self,
                    om_category=obj,
                    funding_source=self.project.default_funding_source
                )

    def clear_empty_om_costs(self):
        self.omcost_set.filter(Q(amount__isnull=True) | Q(amount=0)).filter(description__isnull=True).delete()

    @property
    def dates(self):
        my_str = date(self.start_date)
        if self.end_date:
            my_str += f" &rarr; {date(self.end_date)}"
        return mark_safe(my_str)

    @property
    def deliverables_html(self):
        if self.deliverables:
            return mark_safe(markdown(self.deliverables))

    @property
    def priorities_html(self):
        if self.priorities:
            return mark_safe(markdown(self.priorities))

    def get_project_leads_as_users(self):
        return [s.user for s in self.staff_set.filter(is_lead=True, user__isnull=False)]

    def get_coding(self):
        if self.responsibility_center:
            rc = self.responsibility_center.code
        else:
            rc = "xxxxx"
        if self.allotment_code:
            ac = self.allotment_code.code
        else:
            ac = "xxx"

        # needs to have a value for field "id" before this many-to-many relationship can be used
        if self.id and self.existing_project_codes.exists() >= 1:
            pc = listrify([project_code.code for project_code in self.existing_project_codes.all()])
            if self.existing_project_codes.count() > 1:
                pc = "[" + pc + "]"
        else:
            pc = "xxxxx"
        return "{}-{}-{}".format(rc, ac, pc)

    @property
    def project_codes(self):
        if self.existing_project_codes.exists():
            return listrify(self.existing_project_codes.all())

    def get_funding_sources(self):
        # look through all expenses and allocations and compile a unique list of funding sources
        my_dict = {}
        for item in self.staff_set.all():
            if item.funding_source and item.amount and item.amount > 0:
                my_dict[item.funding_source] = my_dict.get(item.funding_source, 0) + item.amount

        for item in self.omcost_set.all():
            if item.funding_source and item.amount and item.amount > 0:
                my_dict[item.funding_source] = my_dict.get(item.funding_source, 0) + item.amount

        for item in self.capitalcost_set.all():
            if item.funding_source and item.amount and item.amount > 0:
                my_dict[item.funding_source] = my_dict.get(item.funding_source, 0) + item.amount

        for item in self.salaryallocation_set.all():
            if item.funding_source and item.amount and item.amount > 0:
                my_dict[item.funding_source] = my_dict.get(item.funding_source, 0) + item.amount

        for item in self.omallocation_set.all():
            if item.funding_source and item.amount and item.amount > 0:
                my_dict[item.funding_source] = my_dict.get(item.funding_source, 0) + item.amount

        for item in self.capitalallocation_set.all():
            if item.funding_source and item.amount and item.amount > 0:
                my_dict[item.funding_source] = my_dict.get(item.funding_source, 0) + item.amount

        sorted_list = sorted(my_dict.items(), key=lambda item: item[1], reverse=True)
        sorted_list = [tup[0] for tup in sorted_list]
        if self.project.default_funding_source not in sorted_list and self.project.default_funding_source is not None:
            sorted_list.append(self.project.default_funding_source)
        return sorted_list

    @property
    def formatted_status(self):
        return mark_safe(
            f"<span class='{slugify(self.get_status_display())} px-1 py-1'>{self.get_status_display()}</span>"
        )

    def submit(self, request=None):
        if self.status == 1:
            self.submitted = timezone.now()
            self.status = 2
            if request:
                self.modified_by = request.user
            self.save()

    def unsubmit(self, request=None):
        if self.status in [2, 3, 9]:
            self.submitted = None
            self.status = 1
            if request:
                self.modified_by = request.user
            self.save()

    def start_review(self):
        if not hasattr(self, "review"):
            Review.objects.create(project_year=self)

    def remove_review(self):
        if hasattr(self, "review"):
            self.review.delete()

    @property
    def allocated_budget(self):
        return self.review.allocated_budget if hasattr(self, "review") else None

    @property
    def review_score_percentage(self):
        if hasattr(self, "review"):
            return percentage(self.review.score_as_percent, 0)

    @property
    def review_score_fraction(self):
        if hasattr(self, "review"):
            return f'{nz(self.review.total_score, 0)} / {3 * 5}'


class GenericCost(models.Model):
    project_year = models.ForeignKey(ProjectYear, on_delete=models.CASCADE, verbose_name=_("project year"))
    funding_source = models.ForeignKey(FundingSource, on_delete=models.DO_NOTHING, verbose_name=_("funding source"), default=1)
    amount = models.FloatField(default=0, verbose_name=_("amount (CAD)"), blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.amount:
            self.amount = 0
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class GenericAllocation(GenericCost):
    # not actually a cost, but uses same fields
    description = models.TextField(blank=True, null=True, verbose_name=_("description"))

    def __str__(self):
        return f"{self.funding_source}"

    class Meta:
        abstract = True
        ordering = ['funding_source', ]


class OMAllocation(GenericAllocation):
    @property
    def distributed_amount(self):
        amt_dict = OMCost.objects.filter(allocated_source=self).aggregate(Sum('allocated_amount'))
        return amt_dict["allocated_amount__sum"]


class CapitalAllocation(GenericAllocation):
    @property
    def distributed_amount(self):
        amt_dict = CapitalCost.objects.filter(allocated_source=self).aggregate(Sum('allocated_amount'))
        return amt_dict["allocated_amount__sum"]


class SalaryAllocation(GenericAllocation):
    @property
    def distributed_amount(self):
        amt_dict = Staff.objects.filter(allocated_source=self).aggregate(Sum('allocated_amount'))
        return amt_dict["allocated_amount__sum"]


class EmployeeType(SimpleLookup):
    cost_type_choices = [
        (1, _("Salary")),
        (2, _("O&M")),
    ]
    cost_type = models.IntegerField(choices=cost_type_choices)
    exclude_from_rollup = models.BooleanField(default=False)


class Level(SimpleLookup):
    pass


class Staff(GenericCost):
    student_program_choices = [
        (1, "FSWEP"),
        (2, "Coop"),
    ]
    employee_type = models.ForeignKey(EmployeeType, on_delete=models.DO_NOTHING, verbose_name=_("employee type"))
    is_lead = models.BooleanField(default=False, verbose_name=_("project lead"), choices=((True, _("yes")), (False, _("no"))))
    is_primary_lead = models.BooleanField(default=False, verbose_name=_("primary project contact"), choices=((True, _("yes")), (False, _("no"))))
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("User"),
                             related_name="staff_instances2")
    name = models.CharField(max_length=255, verbose_name=_("Person name (leave blank if user is selected)"), blank=True, null=True)
    level = models.ForeignKey(Level, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name=_("level"))
    student_program = models.IntegerField(choices=student_program_choices, blank=True, null=True, verbose_name=_("student program"))
    duration_weeks = models.FloatField(default=0, blank=True, null=True, verbose_name=_("duration (weeks)"))
    overtime_hours = models.FloatField(default=0, blank=True, null=True, verbose_name=_("overtime (hours)"))
    overtime_description = models.TextField(blank=True, null=True, verbose_name=_("overtime description"))

    role = models.TextField(blank=True, null=True, verbose_name=_("role in the project"))  # CSRF
    expertise = models.TextField(blank=True, null=True, verbose_name=_("key expertise"))  # CSRF

    allocated_amount = models.FloatField(default=0, verbose_name=_("amount allocated (CAD)"), blank=True, null=True)
    allocated_source = models.ForeignKey(SalaryAllocation, on_delete=models.DO_NOTHING, blank=True, null=True,
                                         verbose_name=_("Allocation Source"))

    def save(self, *args, **kwargs):
        if not self.allocated_amount:
            self.allocated_amount = 0
            self.allocated_source = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.smart_name

    class Meta:
        ordering = ['-is_primary_lead', '-is_lead', 'employee_type', 'level']
        unique_together = [('project_year', 'user'), ]

    @property
    def description(self):
        mystr = f"staff name: {self.smart_name}"
        if self.level:
            mystr += f" ({self.level})"

        if self.student_program:
            mystr += f"\nstudent program: {self.get_student_program_display()}"

        if self.overtime_hours:
            mystr += f"\novertime (hours): {self.overtime_hours}"
            mystr += f"\novertime description: {self.overtime_description}"
        return mystr

    @property
    def smart_name(self):
        if self.user or self.name:
            return self.user.get_full_name() if self.user else self.name
        else:
            return "---"

    def clean(self, *args, **kwargs):
        if self.is_primary_lead:
            if Staff.objects.filter(is_primary_lead=True, project_year=self.project_year).count():
                raise ValidationError("There can only be one primary lead per project year.")
        super(Staff, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.user:
            self.name = None
        super().save(*args, **kwargs)


class OMCategory(models.Model):
    group_choices = (
        (1, _("Travel")),
        (2, _("Equipment Purchase")),
        (3, _("Material and Supplies")),
        (4, _("Human Resources")),
        (5, _("Contracts, Leases, Services")),
        (6, _("Other")),
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    nom = models.CharField(max_length=255, blank=True, null=True)
    group = models.IntegerField(choices=group_choices)

    class Meta:
        ordering = ['group', 'name']

    def __str__(self):
        return f"{self.tname} ({self.get_group_display()})"

    @property
    def tname(self):
        return getattr(self, str(_("name")))


class OMCost(GenericCost):
    om_category = models.ForeignKey(OMCategory, on_delete=models.DO_NOTHING, related_name="om_costs", verbose_name=_("category"))
    description = models.TextField(blank=True, null=True, verbose_name=_("description"))

    allocated_amount = models.FloatField(default=0, verbose_name=_("amount allocated (CAD)"), blank=True, null=True)
    allocated_source = models.ForeignKey(OMAllocation, on_delete=models.DO_NOTHING, blank=True, null=True,
                                         verbose_name=_("Allocation Source"))
    @property
    def category_type(self):
        return self.om_category.get_group_display()

    def save(self, *args, **kwargs):
        if not self.allocated_amount:
            self.allocated_amount = 0
            self.allocated_source = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.om_category}"

    class Meta:
        ordering = ['om_category', ]


class CapitalCost(GenericCost):
    category_choices = (
        (1, _("IM / IT - computers, hardware")),
        (2, _("Lab Equipment")),
        (3, _("Field Equipment")),
        (4, _("Other")),
    )
    category = models.IntegerField(choices=category_choices, verbose_name=_("category"))
    description = models.TextField(blank=True, null=True, verbose_name=_("description"))

    allocated_amount = models.FloatField(default=0, verbose_name=_("amount allocated (CAD)"), blank=True, null=True)
    allocated_source = models.ForeignKey(CapitalAllocation, on_delete=models.DO_NOTHING, blank=True, null=True,
                                         verbose_name=_("Allocation Source"))

    def save(self, *args, **kwargs):
        if not self.allocated_amount:
            self.allocated_amount = 0
            self.allocated_source = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.display

    @property
    def display(self):
        return f"{self.get_category_display()}"

    class Meta:
        ordering = ['category', ]


# TODO: delete me
class GCCost(models.Model):
    project_year = models.ForeignKey(ProjectYear, on_delete=models.CASCADE, related_name="gc_costs", verbose_name=_("project year"))
    recipient_org = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Recipient organization"))
    project_lead = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("project lead"))
    proposed_title = models.CharField(max_length=255, blank=True, null=True,
                                      verbose_name=_("Proposed title of agreement"))
    gc_program = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Name of G&C program"))
    amount = models.FloatField(default=0, verbose_name=_("amount (CAD)"))

    def __str__(self):
        return f"{self.recipient_org} - {self.gc_program}"

    class Meta:
        ordering = ['recipient_org', ]


class Collaboration(models.Model):
    type_choices = (
        (1, _("External Collaborator")),
        (2, _("Grant & Contribution Agreement")),
        (3, _("Collaborative Agreement")),
    )
    new_or_existing_choices = [
        (1, _("New")),
        (2, _("Existing")),
    ]
    project_year = models.ForeignKey(ProjectYear, on_delete=models.CASCADE, related_name="collaborations", verbose_name=_("project year"))
    type = models.IntegerField(choices=type_choices, verbose_name=_("collaboration type"))
    new_or_existing = models.IntegerField(choices=new_or_existing_choices, verbose_name=_("new or existing"))
    organization = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("collaborating organization"))
    people = models.CharField(max_length=1000, verbose_name=_("project lead(s)"), blank=True, null=True)
    critical = models.BooleanField(default=True, verbose_name=_("Critical to project delivery?"), choices=YES_NO_CHOICES)
    agreement_title = models.CharField(max_length=255, verbose_name=_("Title of the agreement"), blank=True, null=True)
    gc_program = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Name of G&C program"))
    amount = models.FloatField(verbose_name=_("Contribution agreement amount"), blank=True, null=True)
    notes = models.TextField(blank=True, null=True, verbose_name=_("notes"))

    class Meta:
        ordering = ['type', 'organization']

    def __str__(self):
        mystr = f"{self.get_type_display()} {self.id}"
        return mystr


# TODO: delete me
class Collaborator(models.Model):
    project_year = models.ForeignKey(ProjectYear, on_delete=models.CASCADE, related_name="collaborators", verbose_name=_("project year"))
    name = models.CharField(max_length=255, verbose_name=_("Name"), blank=True, null=True)
    critical = models.BooleanField(default=True, verbose_name=_("Critical to project delivery"), choices=YES_NO_CHOICES)
    notes = models.TextField(blank=True, null=True, verbose_name=_("notes"))

    class Meta:
        ordering = ['name', ]

    def __str__(self):
        return "{}".format(self.name)


# TODO: delete me
class CollaborativeAgreement(models.Model):
    new_or_existing_choices = [
        (1, _("New")),
        (2, _("Existing")),
    ]
    partner_organization = models.CharField(max_length=255, blank=True, null=True,
                                            verbose_name=_("collaborating organization"))
    project_lead = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("project lead"))
    agreement_title = models.CharField(max_length=255, verbose_name=_("Title of the agreement"), blank=True, null=True)
    new_or_existing = models.IntegerField(choices=new_or_existing_choices, verbose_name=_("new or existing"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("notes"))
    project_year = models.ForeignKey(ProjectYear, on_delete=models.CASCADE, related_name="agreements", verbose_name=_("project year"))

    class Meta:
        ordering = ['partner_organization', ]

    def __str__(self):
        return "{}".format(self.partner_organization)


def file_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'projects/project_{0}/{1}'.format(instance.project.id, filename)


class File(models.Model):
    project = models.ForeignKey(Project, related_name="files", on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255, verbose_name=_("resource name"))
    file = models.FileField(upload_to=file_directory_path, blank=True, null=True, verbose_name=_("file attachment"))
    project_year = models.ForeignKey(ProjectYear, related_name="files", on_delete=models.CASCADE, blank=True, null=True)
    status_report = models.ForeignKey("StatusReport", related_name="files", on_delete=models.CASCADE, blank=True, null=True)
    external_url = models.URLField(blank=True, null=True, verbose_name=_("external URL"))
    date_created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.status_report:
            self.project_year = self.status_report.project_year
            self.project = self.status_report.project_year.project
        elif self.project_year:
            self.project = self.project_year.project
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['project', 'project_year', 'status_report', 'name']

    def __str__(self):
        return self.name

    @property
    def ref(self):
        if self.status_report:
            return str(self.status_report)
        elif self.project_year:
            return str(self.project_year)
        else:
            return "Core project"


class StatusReport(models.Model):
    status_choices = (
        (3, _("On-track")),
        (4, _("Complete")),
        (5, _("Encountering issues")),
        (6, _("Aborted / cancelled")),
    )
    project_year = models.ForeignKey(ProjectYear, related_name="reports", on_delete=models.CASCADE)
    status = models.IntegerField(default=3, editable=True, choices=status_choices)
    major_accomplishments = models.TextField(blank=True, null=True, verbose_name=_("major accomplishments"))
    major_issues = models.TextField(blank=True, null=True, verbose_name=_("major issues encountered"))
    excess_funds = models.BooleanField(default=False, verbose_name=_("do you expect to have unspent funds remaining at the end of the fiscal year?"))
    excess_funds_amt = models.IntegerField(default=0, blank=True, null=True, verbose_name=_("expected amount of unspent funds remaining"))
    excess_funds_comment = models.TextField(blank=True, null=True, verbose_name=_("suggested uses for remaining funds"))
    insuficient_funds = models.BooleanField(default=False, verbose_name=_("do you wish to request additional funding?"))
    insuficient_funds_amt = models.IntegerField(default=0, blank=True, null=True, verbose_name=_("additional funding request amount"))
    insuficient_funds_comment = models.TextField(blank=True, null=True, verbose_name=_("additional funding request description"))
    target_completion_date = models.DateTimeField(blank=True, null=True, verbose_name=_("target completion date"))
    rationale_for_modified_completion_date = models.TextField(blank=True, null=True, verbose_name=_(
        "rationale for a modified completion date"))
    general_comment = models.TextField(blank=True, null=True, verbose_name=_("general comments"))
    section_head_comment = models.TextField(blank=True, null=True, verbose_name=_("section head comment"))
    section_head_reviewed = models.BooleanField(default=False, verbose_name=_("reviewed by section head"), choices=YES_NO_CHOICES)

    # metadata
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="last_mod_by_projects_status_report", blank=True,
                                    null=True, editable=False)

    @property
    def metadata(self):
        return get_metadata_string(self.created_at, None, self.updated_at, self.modified_by)

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['created_at']

    @property
    def report_number(self):
        return [report for report in self.project_year.reports.all().order_by("created_at")].index(self) + 1

    def __str__(self):
        # what is the number of this report?
        return "{}{}".format(
            gettext("Status Report #"),
            self.report_number,
        )

    @property
    def major_accomplishments_html(self):
        if self.major_accomplishments:
            return mark_safe(markdown(self.major_accomplishments))

    @property
    def major_issues_html(self):
        if self.major_issues:
            return mark_safe(markdown(self.major_issues))

    @property
    def excess_funds_comment_html(self):
        if self.excess_funds_comment:
            return mark_safe(markdown(self.excess_funds_comment))

    @property
    def insuficient_funds_comment_html(self):
        if self.insuficient_funds_comment:
            return mark_safe(markdown(self.insuficient_funds_comment))



def ref_mat_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'projects/{filename}'


class Review(models.Model):
    approval_status_choices = (
        (1, _("Approved")),
        (2, _("Recommended")),
        (0, _("Not approved")),
        (9, _("Cancelled")),
    )
    funding_status_choices = (
        (1, _("Fully funded")),
        (2, _("Partially funded")),
        (3, _("Unfunded")),
    )
    approval_level_choices = (
        (1, _("Division-level")),
        (2, _("Branch-level")),
        (3, _("National-level")),
    )
    score_choices = (
        (3, _("High")),
        (2, _("Medium")),
        (1, _("Low")),
    )
    project_year = models.OneToOneField(ProjectYear, related_name="review", on_delete=models.CASCADE)

    collaboration_score = models.IntegerField(blank=True, null=True, verbose_name=_("External Pressures"),
                                              choices=score_choices)
    collaboration_comment = models.TextField(blank=True, null=True, verbose_name=_("External Pressures comments"))

    strategic_score = models.IntegerField(blank=True, null=True, verbose_name=_("Strategic Direction"), choices=score_choices)
    strategic_comment = models.TextField(blank=True, null=True, verbose_name=_("Strategic Direction comments"))

    operational_score = models.IntegerField(blank=True, null=True, verbose_name=_("Operational Considerations"), choices=score_choices)
    operational_comment = models.TextField(blank=True, null=True, verbose_name=_("Operational Considerations comments"))

    ecological_score = models.IntegerField(blank=True, null=True, verbose_name=_("Ecological Impact"), choices=score_choices)
    ecological_comment = models.TextField(blank=True, null=True, verbose_name=_("Ecological Impact comments"))

    scale_score = models.IntegerField(blank=True, null=True, verbose_name=_("scale"), choices=score_choices)
    scale_comment = models.TextField(blank=True, null=True, verbose_name=_("scale comments"))

    general_comment = models.TextField(blank=True, null=True, verbose_name=_("general comments"))
    comments_for_staff = models.TextField(blank=True, null=True, verbose_name=_("questions and comments for project leads"))

    approval_status = models.IntegerField(choices=approval_status_choices, blank=True, null=True, verbose_name=_("Approval status"))
    approval_level = models.IntegerField(choices=approval_level_choices, blank=True, null=True, verbose_name=_("level of approval"))
    funding_status = models.IntegerField(choices=funding_status_choices, blank=True, null=True, verbose_name=_("funding status"))

    allocated_budget = models.FloatField(blank=True, null=True, verbose_name=_("Allocated budget"))
    approval_notification_email_sent = models.DateTimeField(blank=True, null=True, verbose_name=_("Notification Email Sent"), editable=False)
    review_notification_email_sent = models.DateTimeField(blank=True, null=True, verbose_name=_("Notification Email Sent"), editable=False)
    approver_comment = models.TextField(blank=True, null=True, verbose_name=_("Approver comments (shared with project leads)"))

    checklist_file = models.FileField(upload_to=ref_mat_directory_path, verbose_name=_("Feedback Checklist"),
                                      blank=True, null=True)

    # metadata
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="last_mod_by_projects_review", blank=True,
                                         null=True, editable=False)
    modified_by = models.ManyToManyField(User, editable=False)

    # calculated field
    total_score = models.IntegerField(blank=True, null=True, verbose_name=_("total score"), editable=False)

    @property
    def metadata(self):
        try:
            my_str = get_metadata_string(self.created_at, None, self.updated_at, self.last_modified_by)
            if self.modified_by.exists():
                my_str += f"<br><u>Reviewed by:</u> {listrify(self.modified_by.all())}"
            return my_str
        except:
            pass

    def save(self, *args, **kwargs):
        self.total_score = nz(self.collaboration_score, 0) + nz(self.strategic_score, 0) + nz(self.operational_score, 0) + nz(
            self.ecological_score, 0) + nz(self.scale_score, 0)
        super().save(*args, **kwargs)
        if self.last_modified_by:
            self.modified_by.add(self.last_modified_by)

    class Meta:
        ordering = ['created_at']

    @property
    def general_comment_html(self):
        if self.general_comment:
            return mark_safe(markdown(self.general_comment))

    @property
    def score_as_percent(self):
        return nz(self.total_score, 0) / (5 * 3)

    def send_approval_email(self, request):
        email = emails.ProjectApprovalEmail(self, request)
        # send the email object
        custom_send_mail(
            subject=email.subject,
            html_message=email.message,
            from_email=email.from_email,
            recipient_list=email.to_list,
            user=request.user
        )
        self.approval_notification_email_sent = timezone.now()
        self.save()

    def send_review_email(self, request):
        email = emails.ProjectReviewEmail(self, request)
        # send the email object
        custom_send_mail(
            subject=email.subject,
            html_message=email.message,
            from_email=email.from_email,
            recipient_list=email.to_list
        )
        self.review_notification_email_sent = timezone.now()
        self.save()

    def score_html_template(self, score_name):
        score = getattr(self, f'{score_name}_score')
        score_display = getattr(self, f'get_{score_name}_score_display')()
        comment = getattr(self, f'{score_name}_comment')

        my_str = f"<u>{score} ({score_display})</u>"
        if comment:
            my_str += f" &rarr; {comment}"
        return mark_safe(my_str)

    @property
    def collaboration_score_html(self):
        return self.score_html_template("collaboration")

    @property
    def strategic_score_html(self):
        return self.score_html_template("strategic")

    @property
    def operational_score_html(self):
        return self.score_html_template("operational")

    @property
    def ecological_score_html(self):
        return self.score_html_template("ecological")

    @property
    def scale_score_html(self):
        return self.score_html_template("scale")


class Activity(models.Model):
    type_choices = (
        (1, _("Milestone")),
        (2, _("Deliverable")),
    )
    likelihood_choices = (
        (1, _("1-Very unlikely")),
        (2, _("2-Unlikely")),
        (3, _("3-Low")),
        (4, _("4-Likely")),
        (5, _("5-Almost certain")),
    )
    impact_choices = (
        (1, _("1-Negligible")),
        (2, _("2-Low")),
        (3, _("3-Medium")),
        (4, _("4-High")),
        (5, _("5-Extreme")),
    )
    risk_rating_choices = (
        (None, "n/a"),
        (1, _("Low")),
        (2, _("Medium")),
        (3, _("High")),
    )

    project_year = models.ForeignKey(ProjectYear, related_name="activities", on_delete=models.CASCADE)
    type = models.IntegerField(choices=type_choices, verbose_name="Milestone or Deliverable?")
    classification = models.ForeignKey(ActivityClassification, blank=True, null=True, on_delete=models.DO_NOTHING, verbose_name=_("Type"))
    name = models.CharField(max_length=500, verbose_name=_("name"))
    target_start_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Target start date (optional)"))
    target_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Target end date (optional)"))
    description = models.TextField(blank=True, null=True, verbose_name=_("description"))
    responsible_parties = models.ManyToManyField(User, blank=True, verbose_name=_("responsible parties"))
    responsible_party = models.CharField(max_length=500, verbose_name=_("responsible party notes"), blank=True, null=True)

    risk_description = models.TextField(blank=True, null=True, verbose_name=_("Description of risks and their consequences"))  # CSRF and ACRDP
    impact = models.IntegerField(choices=impact_choices, blank=True, null=True, verbose_name=_("what will be the impact if the risks occurs"))  # ACRDP
    likelihood = models.IntegerField(choices=likelihood_choices, blank=True, null=True,
                                     verbose_name=_("what is the likelihood of the risks occurring"))  # ACRDP
    risk_rating = models.IntegerField(choices=risk_rating_choices, blank=True, null=True, editable=False)  # ACRDP
    mitigation_measures = models.TextField(blank=True, null=True, verbose_name=_("what measures will be used to mitigate the risks"))  # CSRF and ACRDP
    parent = models.ForeignKey("Activity", related_name="children", on_delete=models.CASCADE, verbose_name=_("parent activity"), blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.impact and self.likelihood:
            self.risk_rating = get_risk_rating(self.impact, self.likelihood)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['project_year', 'target_start_date', 'target_date', 'name']

    def __str__(self):
        return self.name

    @property
    def latest_update(self):
        return self.updates.first()

    @property
    def dates(self):
        # if there is just an end date, we should display politely
        my_str = "??"
        if self.target_date and not self.target_start_date:
            my_str = _("ending {date}").format(date=date(self.target_date))
        elif not self.target_date and self.target_start_date:
            my_str = _("starting {date}").format(date=date(self.target_start_date))
        elif self.target_start_date and self.target_date:
            my_str = f"{date(self.target_start_date)} &rarr;<br> {date(self.target_date)}"
        return mark_safe(my_str)


class ActivityUpdate(MetadataFields):
    status_choices = (
        (7, _("In progress")),
        (8, _("Completed")),
        (9, _("Aborted / cancelled")),
    )
    activity = models.ForeignKey(Activity, related_name="updates", on_delete=models.CASCADE)
    status_report = models.ForeignKey(StatusReport, related_name="updates", on_delete=models.CASCADE)
    status = models.IntegerField(default=7, choices=status_choices)
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))

    class Meta:
        ordering = ['-status_report', 'status']
        unique_together = [('activity', 'status_report'), ]

    def __str__(self):
        # what is the number of this report?
        return "{} {}".format(
            gettext("Update on "),
            self.activity,
        )

    @property
    def notes_html(self):
        if self.notes:
            return mark_safe(markdown(self.notes))


class ReferenceMaterial(SimpleLookup):
    file_en = models.FileField(upload_to=ref_mat_directory_path, verbose_name=_("file attachment (English)"))
    file_fr = models.FileField(upload_to=ref_mat_directory_path, verbose_name=_("file attachment (French)"), blank=True, null=True)
    region = models.ForeignKey(shared_models.Region, on_delete=models.DO_NOTHING, related_name="reference_materials2",
                               verbose_name=_("region"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    @property
    def metadata(self):
        return get_metadata_string(self.created_at, None, self.updated_at)

    @property
    def file_display_fr(self):
        if self.file_fr:
            return mark_safe(
                f"<a href='{self.file_fr.url}'> <span class='mdi mdi-file text-primary'></span></a>"
            )

    class Meta:
        ordering = ["region", "-updated_at"]


class StorageSolution(SimpleLookup):
    pass


class DMA(MetadataFields):
    status_choices = (
        (0, _("Unevaluated")),
        (1, _("On-track")),
        (2, _("Complete")),
        (3, _("Encountering issues")),
        (4, _("Aborted / cancelled")),
        (5, _("Pending new evaluation")),
    )
    frequency_choices = (
        (1, _("Daily")),
        (2, _("Weekly")),
        (3, _("Monthly")),
        (4, _("Annually")),
        (5, _("Irregular / as needed")),
        (9, _("Other")),
    )
    status = models.IntegerField(default=3, editable=False, choices=status_choices)
    project = models.ForeignKey(Project, related_name="reports", on_delete=models.CASCADE)

    # Identification
    title = models.CharField(max_length=1000, verbose_name=_("Title"), help_text=_("What is the title of the Data Management Agreement?"))
    data_contact = models.CharField(max_length=500, blank=True, null=True, verbose_name=_("Who is the principal steward of this data?"),
                                    help_text=_("i.e., who is the primary responsible party?"))

    # Metadata
    metadata_contact = models.CharField(max_length=500, blank=True, null=True, verbose_name=_("Who is responsible for creating and maintaining the metadata?"),
                                        help_text=_("i.e., who is responsible for keeping metadata records up-to-date?"))
    metadata_tool = models.TextField(blank=True, null=True, verbose_name=_("Describe the tools or processes that will be used to create metadata"),
                                     help_text=_(
                                         "e.g., Metadata Inventory app in DM Apps, DFO Enterprise Data Hub, Federal Geospatial Portal, stand-alone file, ..."))
    metadata_url = models.CharField(blank=True, null=True, max_length=1000, verbose_name=_("Please provide any URLs to the metadata"),
                                    help_text=_("Full link to any metadata records available online, if applicable"))
    metadata_update_freq = models.IntegerField(blank=True, null=True, verbose_name=_("At what frequency should the metadata be updated? "),
                                               help_text=_("What should be the expectation for how often the metadata is updated?"), choices=frequency_choices)
    metadata_freq_text = models.TextField(blank=True, null=True, verbose_name=_("Justification for frequency:"),
                                          help_text=_("What justification can be provided for the above selection?"))

    # Archiving / Storage
    storage_solutions = models.ManyToManyField(StorageSolution, blank=True, verbose_name=_(
        "Which storage solution(s) will be used to house the raw field data, processed data, and all other data products?"))
    storage_solution_text = models.TextField(blank=True, null=True, verbose_name=_("Justification for selection of storage solution(s)"),
                                             help_text=_("Provide your rational for the selection(s) made above."))
    storage_needed = models.TextField(blank=True, null=True, verbose_name=_("What is the estimated storage space needed for the above?"),
                                      help_text=_("This includes raw field data, processed data, and all other data products etc.)"))
    raw_data_retention = models.TextField(blank=True, null=True, verbose_name=_("What is the retention policy for the raw field data?"), help_text=_(
        "This would include instrument data, field sheets, physical samples etc. Please refer to the DFO EOS Retention Policy for clarification)"))
    data_retention = models.TextField(blank=True, null=True, verbose_name=_("What is the retention policy for the data?"),
                                      help_text=_("Please refer to the DFO EOS Retention Policy for clarification."))
    backup_plan = models.TextField(blank=True, null=True, verbose_name=_("What procedures will be taken to back-up/secure the data?"))
    cloud_costs = models.TextField(blank=True, null=True,
                                   verbose_name=_("If using cloud storage, what is the estimated annual cost and who will be covering the cost? "),
                                   help_text=_(
                                       "e.g., cloud storage is estimated at $1000/yr and will be paid for under the the division manager's budget"))

    # Sharing
    had_sharing_agreements = models.BooleanField(default=False, verbose_name=_("Is the dataset subject to a data sharing agreement, MOU, etc.?"),
                                                 choices=YES_NO_CHOICES)
    sharing_agreements_text = models.TextField(blank=True, null=True, verbose_name=_("If yes, who are the counterparts for the agreement(s)?"),
                                               help_text=_("please provide the name of the organization and the primary contact for each agreement."))
    publication_timeframe = models.TextField(blank=True, null=True, verbose_name=_("How soon after data collection will data be made available?"),
                                             help_text=_("The answer provided will set the expectation for the open data publication frequency"))
    publishing_platforms = models.TextField(blank=True, null=True, verbose_name=_("Which open data publishing mechanism(s) will be used?"), help_text=_(
        "The best option is the Government of Canada's Open Data Platform however other platforms / publications are acceptable provided they are"
        " freely available to the general public."))
    comments = models.TextField(blank=True, null=True, verbose_name=_("Additional comments to take into consideration (if applicable):"))

    class Meta:
        verbose_name = _("Data Management Agreement")
        ordering = ["project__section__division__branch__sector__region", "project__section__division", "project__section"]

    def get_absolute_url(self):
        return reverse('ppt:dma_detail', args=[self.id])

    def save(self, *args, **kwargs):
        # set the status...
        if not self.reviews.exists():
            self.status = 0  # unevaluated
        else:
            last_review = self.reviews.last()
            if last_review.is_final_review:
                self.status = 2  # complete
            elif last_review.decision == 1:  # compliant
                self.status = 1  # on-track
                # but wait, what if this is an old evaluation?
                # if the review was more than six months old, set the status to 5
                if (timezone.now() - last_review.created_at).days > (28*6):
                    self.status = 5  # pending evaluation

            elif last_review.decision == 2:  # non-compliant
                self.status = 3  # encountering issues

        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class DMAReview(MetadataFields):
    decision_choices = (
        (0, _("Unevaluated")),
        (1, _("Compliant")),
        (2, _("Non-compliant")),
    )
    dma = models.ForeignKey(DMA, related_name="reviews", on_delete=models.CASCADE)
    fiscal_year = models.ForeignKey(shared_models.FiscalYear, related_name="ppt_dma_reviews", on_delete=models.DO_NOTHING,
                                    default=fiscal_year(timezone.now(), sap_style=True))
    decision = models.IntegerField(default=0, choices=decision_choices)
    is_final_review = models.BooleanField(default=False, verbose_name=_("Will this be the final review of this agreement?"),
                                          help_text=_("If so, please make sure to provide an explanation in the comments field."))
    comments = models.TextField(blank=True, null=True, verbose_name=_("comments"))

    class Meta:
        ordering = ["fiscal_year", '-created_at']
        unique_together = [
            ('dma', 'fiscal_year'),  # there should only be a single review per year on a given DMA
        ]

    @property
    def comments_html(self):
        if self.comments:
            return mark_safe(markdown(self.comments))
