from datetime import timedelta

import pandas as pd
from django.db.models import Sum, Q
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.utils.translation import gettext as _, gettext_lazy

from lib.templatetags.custom_filters import nz
from shared_models import models as shared_models
from . import models


def get_help_text_dict(model=None):
    my_dict = {}
    if not model:
        for obj in models.HelpText.objects.all():
            my_dict[obj.field_name] = str(obj)
    else:
        # If a model is supplied get the fields specific to that model
        for obj in models.HelpText.objects.filter(model=str(model.__name__)):
            my_dict[obj.field_name] = str(obj)

    return my_dict


def ajax_get_fields(request):
    model_name = request.GET.get('model', None)

    # use the model name passed from the web page to find the model in the apps models file
    model = models.__dict__[model_name]

    # use the retrieved model and get the doc string which is a string in the format
    # SomeModelName(id, field1, field2, field3)
    # remove the trailing parentheses, split the string up based on ', ', then drop the first element
    # which is the model name and the id.
    match = str(model.__dict__['__doc__']).replace(")", "").split(", ")[1:]
    fields = list()
    for f in match:
        label = "---"
        attr = getattr(model, f).field
        if hasattr(attr, 'verbose_name'):
            label = attr.verbose_name

        fields.append([f, label])

    data = {
        'fields': fields
    }

    return JsonResponse(data)


def toggle_help_text_edit(request, user_id):
    usr = User.objects.get(pk=user_id)

    user_mode = None
    # mode 1 is read only
    mode = 1
    if models.PPTAdminUser.objects.filter(user=usr):
        user_mode = models.PPTAdminUser.objects.get(user=usr)
        mode = user_mode.mode

    # fancy math way of toggling between 1 and 2
    mode = (mode % 2) + 1

    if not user_mode:
        user_mode = models.PPTAdminUser(user=usr)

    user_mode.mode = mode
    user_mode.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))



def in_ppt_regional_admin_group(user):
    # make sure the following group exist:
    if user:
        return bool(hasattr(user, "ppt_admin_user") and user.ppt_admin_user.region)


def in_ppt_national_admin_group(user):
    # make sure the following group exist:
    if user:
        return bool(hasattr(user, "ppt_admin_user") and user.ppt_admin_user.is_national_admin)


def in_ppt_admin_group(user):
    """
    Will return True if user is in project_admin group
    """
    if user:
        return in_ppt_regional_admin_group(user) or in_ppt_national_admin_group(user)


def is_service_coordinator(user):
    """
    Will return True if user is ppt service coordinator
    """
    return user.services.exists()


def is_management(user):
    """
        Will return True if user is in project_admin group, or if user is listed as a head of a section, division or branch
    """
    if user and user.id:
        return shared_models.Section.objects.filter(head=user).exists() or \
               shared_models.Division.objects.filter(head=user).exists() or \
               shared_models.Branch.objects.filter(head=user).exists()


def is_management_or_admin(user):
    """
        Will return True if user is in project_admin group, or if user is listed as a head of a section, division or branch
    """
    if user.id:
        return in_ppt_admin_group(user) or is_management(user) or is_service_coordinator(user)


def is_section_head(user, project):
    try:
        return True if project.section.head == user else False
    except AttributeError as e:
        # print(e)
        pass


def is_division_manager(user, project):
    try:
        return True if project.section.division.head == user else False
    except AttributeError:
        pass


def is_rds(user, project=None):
    if project:
        try:
            return True if project.section.division.branch.head == user else False
        except AttributeError:
            pass
    else:
        return shared_models.Branch.objects.filter(head=user).exists()


def is_project_lead(user, project_id=None, project_year_id=None):
    """
    returns True if user is among the project's project leads
    """
    if user.id:
        project = None
        if project_year_id:
            project = models.ProjectYear.objects.get(pk=project_year_id).project
        elif project_id:
            project = models.Project.objects.get(pk=project_id)

        if project:
            return user in [s.user for s in models.Staff.objects.filter(project_year__project=project, is_lead=True)]


def can_modify_project(user, project_id, return_as_dict=False):
    """
    returns True if user has permissions to delete or modify a project
    The answer of this question will depend on whether the project is submitted. Project leads cannot edit a submitted project
    """
    my_dict = dict(can_modify=False, reason=_("You are not logged in"))

    if user.id:

        my_dict["reason"] = "You are not a project lead or manager of this project"
        project = models.Project.objects.get(pk=project_id)

        # check to see if a superuser or projects_admin -- both are allow to modify projects
        if in_ppt_national_admin_group(user):
            my_dict["reason"] = "You can modify this record because you are a National PPT Administrator"
            my_dict["can_modify"] = True
        elif in_ppt_regional_admin_group(user) and project.section and project.section.division.branch.sector.region == user.ppt_admin_user.region:
            my_dict["reason"] = f"You can modify this record because you are a {user.ppt_admin_user.region} Regional Administrator"
            my_dict["can_modify"] = True

        # check to see if service owner (if there an overlap between the services on a project year and the services for a user)
        elif user.services.exists() and \
                len(list(set(s.id for s in user.services.all()) & set(s.id for s in models.Service.objects.filter(years__project=project).all()))):
            my_dict["reason"] = f"You can modify this record because you are a service coordinator for a service that is listed on a project year."
            my_dict["can_modify"] = True

        # check to see if they are a section head
        elif is_section_head(user, project):
            my_dict["reason"] = "You can modify this record because it falls under your section"
            my_dict["can_modify"] = True

        # check to see if they are a div. manager
        elif is_division_manager(user, project):
            my_dict["reason"] = "You can modify this record because it falls under your division"
            my_dict["can_modify"] = True

        # check to see if they are an RDS
        elif is_rds(user, project):
            my_dict["reason"] = "You can modify this record because it falls under your branch"
            my_dict["can_modify"] = True

        # check to see if they are a project lead
        elif is_project_lead(user, project_id=project.id):
            my_dict["reason"] = "You can modify this record because you are a project lead"
            my_dict["can_modify"] = True

        # check to see if they are a project lead
        elif not models.Staff.objects.filter(project_year__project=project, is_lead=True).exists():
            my_dict["reason"] = "You can modify this record because there are currently no project leads"
            my_dict["can_modify"] = True

        return my_dict if return_as_dict else my_dict["can_modify"]


def is_admin_or_project_manager(user, project):
    """returns True if user is either in 'projects_admin' group OR if they are a manager of the project (section head, div. manager, RDS)"""
    if user.id:

        # check to see if a superuser or projects_admin -- both are allow to modify projects
        if in_ppt_admin_group(user):
            return True

        # check to see if they are a section head, div. manager or RDS
        if is_section_head(user, project) or is_division_manager(user, project) or is_rds(user, project):
            return True


def get_manageable_sections(user):
    if in_ppt_national_admin_group(user):
        return shared_models.Section.objects.filter(ppt__isnull=False).distinct()
    elif in_ppt_regional_admin_group(user):
        return shared_models.Section.objects.filter(division__branch__sector__region=user.ppt_admin_user.region)
    return shared_models.Section.objects.filter(Q(head=user) | Q(division__head=user) | Q(division__branch__head=user))


def get_section_choices(all=False, full_name=True, region_filter=None, division_filter=None):
    if full_name:
        my_attr = "full_name"
    else:
        my_attr = _("name")

    if region_filter:
        reg_kwargs = {
            "division__branch__region_id": region_filter
        }
    else:
        reg_kwargs = {
            "division__branch__region_id__isnull": False
        }

    if division_filter:
        div_kwargs = {
            "division_id": division_filter
        }
    else:
        div_kwargs = {
            "division_id__isnull": False
        }

    if not all:
        my_choice_list = [(s.id, getattr(s, my_attr)) for s in
                          shared_models.Section.objects.all().order_by(
                              "division__branch__region",
                              "division__branch",
                              "division",
                              "name"
                          ).filter(**div_kwargs).filter(**reg_kwargs) if s.ppt.count() > 0]
    else:
        my_choice_list = [(s.id, getattr(s, my_attr)) for s in
                          shared_models.Section.objects.filter(
                          ).order_by(
                              "division__branch__region",
                              "division__branch",
                              "division",
                              "name"
                          ).filter(**div_kwargs).filter(**reg_kwargs)]

    return my_choice_list


def get_division_choices(all=False, region_filter=None):
    division_list = set(
        [shared_models.Section.objects.get(pk=s[0]).division_id for s in get_section_choices(all=all, region_filter=region_filter)])
    return [(d.id, str(d)) for d in
            shared_models.Division.objects.filter(id__in=division_list).order_by("branch__region", "name")]


def get_region_choices(all=False):
    region_list = set(
        [shared_models.Division.objects.get(pk=d[0]).branch.region_id for d in get_division_choices(all=all)])
    return [(r.id, str(r)) for r in
            shared_models.Region.objects.filter(id__in=region_list).order_by("name", )]


def get_omcatagory_choices():
    return [(o.id, str(o)) for o in models.OMCategory.objects.all()]


def get_funding_sources(all=False):
    return [(fs.id, str(fs)) for fs in models.FundingSource.objects.all()]


def get_user_fte_breakdown(user, fiscal_year_id, staff_instance_qs=None, fiscal_year=None, filtered_si_qs=None):
    if staff_instance_qs:
        staff_instances = staff_instance_qs
    else:
        staff_instances = models.Staff.objects.filter(user=user, project_year__fiscal_year_id=fiscal_year_id)\
            .select_related("project_year", "level", "employee_type", "funding_source")
    my_dict = dict()
    my_dict['name'] = f"{user.last_name}, {user.first_name}"
    employee_type_qs = staff_instances.filter(employee_type__isnull=False).values_list('employee_type__name', flat=True)
    if employee_type_qs:
        # call to set is for uniqueness
        my_dict['employee_type'] = ", ".join(list(set(employee_type_qs)))
    else:
        my_dict['employee_type'] = ""

    level_qs = staff_instances.filter(level__isnull=False).values_list('level__name', flat=True)
    if level_qs:
        # call to set is for uniqueness
        my_dict['level'] = ", ".join(list(set(level_qs)))
    else:
        my_dict['level'] = ""

    funding_qs = staff_instances.filter(funding_source__isnull=False)
    funding_list = [staff.funding_source.__str__() for staff in funding_qs]
    # call to set is for uniqueness
    if funding_list:
        my_dict['funding'] = ", ".join(list(set(funding_list)))
    else:
        my_dict['funding'] = ""

    my_dict["section"] = ""
    if user.profile.section:
        my_dict["section"] = "{}, {}".format(user.profile.section.name, str(user.profile.section.head or ''))

    if fiscal_year:
        my_dict['fiscal_year'] = str(fiscal_year)
    else:
        my_dict['fiscal_year'] = str(shared_models.FiscalYear.objects.get(pk=fiscal_year_id))
    my_dict['draft'] = nz(staff_instances.filter(
        project_year__status=1
    ).aggregate(dsum=Sum("duration_weeks"))["dsum"], 0)

    my_dict['submitted_unapproved'] = nz(staff_instances.filter(
        project_year__status__in=[2, 3, 6]
    ).aggregate(dsum=Sum("duration_weeks"))["dsum"], 0)

    my_dict['approved'] = nz(staff_instances.filter(
        project_year__status=4
    ).aggregate(dsum=Sum("duration_weeks"))["dsum"], 0)

    if filtered_si_qs:
        my_dict['filtered_draft'] = nz(filtered_si_qs.filter(
            project_year__status=1
        ).aggregate(dsum=Sum("duration_weeks"))["dsum"], 0)

        my_dict['filtered_submitted_unapproved'] = nz(filtered_si_qs.filter(
            project_year__status__in=[2, 3, 6]
        ).aggregate(dsum=Sum("duration_weeks"))["dsum"], 0)

        my_dict['filtered_approved'] = nz(filtered_si_qs.filter(
            project_year__status=4
        ).aggregate(dsum=Sum("duration_weeks"))["dsum"], 0)
    else:
        my_dict['filtered_draft'] = None
        my_dict['filtered_submitted_unapproved'] = None
        my_dict['filtered_approved'] = None
    return my_dict


def financial_project_year_summary_data(project_year):
    """ this function will return a list, where each row corresponds to a funding source"""
    # for every funding source, we will want to summarize: Salary, O&M, Capital and TOTAL
    my_list = []

    for fs in project_year.get_funding_sources():
        my_dict = dict()
        my_dict["type"] = fs.get_funding_source_type_display()
        my_dict["name"] = str(fs)
        my_dict["salary"] = 0
        my_dict["om"] = 0
        my_dict["capital"] = 0

        # first calc for staff
        for staff in project_year.staff_set.filter(funding_source=fs):
            # exclude any employees that should be excluded. This is a fail safe since the form should prevent data entry
            if not staff.employee_type.exclude_from_rollup:
                if staff.employee_type.cost_type == 1:
                    my_dict["salary"] += nz(staff.amount, 0)
                elif staff.employee_type.cost_type == 2:
                    my_dict["om"] += nz(staff.amount, 0)

        # O&M costs
        for cost in project_year.omcost_set.filter(funding_source=fs):
            my_dict["om"] += nz(cost.amount, 0)

        # Capital costs
        for cost in project_year.capitalcost_set.filter(funding_source=fs):
            my_dict["capital"] += nz(cost.amount, 0)

        my_dict["total_in_om"] = models.SALARY_TO_OM_FACTOR * my_dict["salary"] + my_dict["om"] + my_dict["capital"]

        my_list.append(my_dict)

    return my_list


def financial_project_summary_data(project):
    my_list = []
    funding_source_list = project.get_funding_sources()
    if funding_source_list:
        for fs in funding_source_list:
            my_dict = dict()
            my_dict["type"] = fs.get_funding_source_type_display()
            my_dict["name"] = str(fs)
            my_dict["salary"] = 0
            my_dict["om"] = 0
            my_dict["capital"] = 0
            my_dict["allocated_salary"] = 0
            my_dict["allocated_om"] = 0
            my_dict["allocated_capital"] = 0

            # first calc for staff
            for staff in models.Staff.objects.filter(funding_source=fs, project_year__project=project):
                # Split staff based on om vs salary type
                if not staff.employee_type.exclude_from_rollup:
                    if staff.employee_type.cost_type == 1:
                        my_dict["salary"] += nz(staff.amount, 0)
                    elif staff.employee_type.cost_type == 2:
                        my_dict["om"] += nz(staff.amount, 0)

            # O&M costs
            for cost in models.OMCost.objects.filter(funding_source=fs, project_year__project=project):
                my_dict["om"] += nz(cost.amount, 0)

            # Capital costs
            for cost in models.CapitalCost.objects.filter(funding_source=fs, project_year__project=project):
                my_dict["capital"] += nz(cost.amount, 0)

            my_dict["total_in_om"] = models.SALARY_TO_OM_FACTOR * my_dict["salary"] + my_dict["om"] + my_dict["capital"]

            # allocated funds:
            for review in models.Review.objects.filter(project_year__project=project):
                if project.default_funding_source == fs:
                    my_dict["allocated_om"] += nz(review.allocated_budget, 0)
            my_dict["allocated_total_in_om"] = my_dict["allocated_om"]

            my_list.append(my_dict)

    return my_list


def get_py_funding_source_details(project_year, funding_source):
    py_dict = dict()
    py_dict["id"] = project_year.id
    py_dict["project"] = {"id": project_year.project.id}
    py_dict["has_fs"] = False
    py_dict["capital"] = 0
    py_dict["om"] = 0
    py_dict["salary"] = 0
    py_dict["allocated_capital"] = 0
    py_dict["allocated_om"] = 0
    py_dict["allocated_salary"] = 0
    py_dict["allocated_om_allocations"] = 0
    py_dict["status_display"] = project_year.formatted_status
    py_dict["year_display"] = str(project_year.fiscal_year)
    py_dict["title"] = project_year.project.title
    py_dict["section"] = str(project_year.project.section)

    if funding_source in project_year.get_funding_sources():
        py_dict["has_fs"] = True

    # Capital costs
    for cost in models.CapitalCost.objects.filter(funding_source=funding_source, project_year=project_year):
        py_dict["capital"] += nz(cost.amount, 0)

    # Salary + OM costs:
    for cost in models.OMCost.objects.filter(funding_source=funding_source, project_year=project_year):
        py_dict["om"] += nz(cost.amount, 0)

    for staff in models.Staff.objects.filter(funding_source=funding_source, project_year=project_year):
        if not staff.employee_type.exclude_from_rollup:
            if staff.employee_type.cost_type == 1:
                py_dict["salary"] += nz(staff.amount, 0)
            elif staff.employee_type.cost_type == 2:
                py_dict["om"] += nz(staff.amount, 0)

    for allocation in models.CapitalAllocation.objects.filter(funding_source=funding_source, project_year=project_year):
        py_dict["allocated_capital"] += nz(allocation.amount, 0)

    for allocation in models.OMAllocation.objects.filter(funding_source=funding_source, project_year=project_year):
        # this is what will get used, once the allocated budget field is removed from approvals.
        py_dict["allocated_om_allocations"] += nz(allocation.amount, 0)

    for allocation in models.SalaryAllocation.objects.filter(funding_source=funding_source, project_year=project_year):
        py_dict["allocated_salary"] += nz(allocation.amount, 0)

    if hasattr(project_year, "review"):
        if project_year.project.default_funding_source == funding_source:
            py_dict["allocated_om"] += nz(project_year.review.allocated_budget, 0)

    return py_dict


def multiple_financial_project_year_summary_data(project_years):
    my_list = []

    # select related fields:
    project_years = project_years.select_related("project", "project__section", "fiscal_year")\
        .prefetch_related('staff_set__funding_source',
                          'omcost_set__funding_source',
                          'capitalcost_set__funding_source',
                          'salaryallocation_set__funding_source',
                          'omallocation_set__funding_source',
                          'capitalallocation_set__funding_source')

    fs_list = list()
    # first get funding source list
    for py in project_years:
        fs_list.extend([fs.id for fs in py.get_funding_sources()])
    funding_sources = models.FundingSource.objects.filter(id__in=fs_list)

    for fs in funding_sources:
        fs_dict = dict()
        fs_dict["type"] = fs.get_funding_source_type_display()
        fs_dict["name"] = str(fs)
        fs_dict["py_count"] = 0

        fs_dict["salary"] = 0
        fs_dict["allocated_salary"] = 0
        fs_dict["salary_pys"] = []

        fs_dict["om"] = 0
        fs_dict["allocated_om"] = 0
        fs_dict["om_pys"] = []

        fs_dict["capital"] = 0
        fs_dict["allocated_capital"] = 0
        fs_dict["capital_pys"] = []

        for py in project_years:
            py_financial_dict = get_py_funding_source_details(py, fs)
            if py_financial_dict["has_fs"]:
                fs_dict["py_count"] += 1
                financial_categories = ["om", "capital", "salary"]
                for financial_category in financial_categories:
                    # sum finances from all project years, for each category
                    if py_financial_dict[financial_category]:
                        fs_dict[financial_category] += py_financial_dict[financial_category]
                        if py_financial_dict not in fs_dict["{}_pys".format(financial_category)]:
                            fs_dict["{}_pys".format(financial_category)].append(py_financial_dict)
                    if py_financial_dict["allocated_{}".format(financial_category)]:
                        fs_dict["allocated_{}".format(financial_category)] += py_financial_dict["allocated_{}".format(financial_category)]
                        if py_financial_dict not in fs_dict["{}_pys".format(financial_category)]:
                            fs_dict["{}_pys".format(financial_category)].append(py_financial_dict)

        fs_dict["total_in_om"] = models.SALARY_TO_OM_FACTOR * fs_dict["salary"] + fs_dict["om"] + fs_dict["capital"]
        fs_dict["allocated_total_in_om"] = models.SALARY_TO_OM_FACTOR * fs_dict["allocated_salary"] + fs_dict["allocated_om"] + fs_dict["allocated_capital"]

        my_list.append(fs_dict)

    return my_list


def get_project_field_list(project):
    is_acrdp = project.is_acrdp
    is_csrf = project.is_csrf
    is_sara = project.is_sara
    general_project = not is_csrf and not is_acrdp and not is_sara

    my_list = [
        'id',
        'section',
        # 'title',
        'overview' if general_project else None,
        # do not call the html field directly or we loose the ability to get the model's verbose name
        'activity_type',
        'functional_group.theme|{}'.format(_("theme")),
        'functional_group',
        'default_funding_source',
        'start_date',
        'end_date',
        'fiscal_years|{}'.format(_("Project years")),
        'funding_sources',
        'lead_staff',
        'is_hidden',

        # acrdp fields
        'overview|{}'.format(gettext_lazy("Project overview / ACRDP objectives")) if is_acrdp else None,
        'organization' if is_acrdp else None,
        'species_involved' if is_acrdp else None,
        'team_description_html|{}'.format(_("description of team and required qualifications (ACRDP)")) if is_acrdp else None,
        'rationale_html|{}'.format(_("project problem / rationale (ACRDP)")) if is_acrdp else None,
        'experimental_protocol_html|{}'.format(_("experimental protocol (ACRDP)")) if is_acrdp else None,

        # csrf fields
        'overview' if is_csrf else None,
        'csrf_fiscal_year|{}'.format(_("CSRF Application Year")) if is_csrf else None,
        'csrf_theme|{}'.format(_("CSRF Research Area")) if is_csrf else None,
        'csrf_sub_theme|{}'.format(_("CSRF Research Field")) if is_csrf else None,
        'csrf_priority|{}'.format(_("CSRF Research priority")) if is_csrf else None,
        'client_information_html|{}'.format(_("Specific Client Question")) if is_csrf else None,
        'second_priority' if is_csrf else None,
        'objectives_html|{}'.format(_("project objectives (CSRF)")) if is_csrf else None,
        'innovation_html|{}'.format(_("innovation (CSRF)")) if is_csrf else None,
        'other_funding_html|{}'.format(_("other sources of funding (CSRF)")) if is_csrf else None,

        # sara fields
        'overview|{}'.format(_("Objectives and methods")) if is_sara else None,
        'reporting_mechanism' if is_sara else None,
        'future_funding_needs' if is_sara else None,

        'tags',
        'dmas',
        'references',
        'csas_processes',
        'metadata|{}'.format(_("metadata")),
    ]
    while None in my_list: my_list.remove(None)
    return my_list


def get_project_year_field_list(project_year=None):
    my_list = [
        'dates|dates',
        'priorities',  # do not call the html field directly or we loose the ability to get the model's verbose name
        'services|{}'.format(_("services required")),

        # SPECIALIZED EQUIPMENT COMPONENT
        #################################
        'requires_specialized_equipment|{}'.format(_("requires specialized equipment?")),
        'technical_service_needs' if not project_year or project_year.requires_specialized_equipment else None,
        'mobilization_needs' if not project_year or project_year.requires_specialized_equipment else None,

        # FIELD COMPONENT
        #################
        'has_field_component|{}'.format(_("has field component?")),
        'vehicle_needs' if not project_year or project_year.has_field_component else None,
        'has_ship_needs' if not project_year or project_year.has_field_component else None,
        'ship_needs' if not project_year or (project_year.has_field_component and project_year.has_ship_needs) else None,
        'coip_reference_id' if not project_year or (project_year.has_field_component and project_year.has_ship_needs) else None,
        'instrumentation' if not project_year or project_year.has_field_component else None,
        'owner_of_instrumentation' if not project_year or project_year.has_field_component else None,
        'requires_field_staff' if not project_year or project_year.has_field_component else None,
        'field_staff_needs' if not project_year or project_year.has_field_component and project_year.requires_field_staff else None,

        # DATA COMPONENT
        ################
        'has_data_component',
        'data_collected' if not project_year or project_year.has_data_component else None,
        'data_products' if not project_year or project_year.has_data_component else None,
        'open_data_eligible' if not project_year or project_year.has_data_component else None,
        'data_storage_plan' if not project_year or project_year.has_data_component else None,
        'data_management_needs' if not project_year or project_year.has_data_component else None,

        # LAB COMPONENT
        ###############
        'has_lab_component',
        'requires_lab_space' if not project_year or project_year.has_lab_component else None,
        'requires_other_lab_support' if not project_year or project_year.has_lab_component else None,
        'other_lab_support_needs' if not project_year or project_year.has_lab_component else None,

        'it_needs|{}'.format(_("special IT requirements")),
        'additional_notes',
        'project_codes|{}'.format(_("project codes")),
        'submitted',
        'formatted_status|{}'.format(_("status")),
        # 'allocated_budget|{}'.format(_("allocated budget")),
        # 'review_score|{}'.format(_("review score")),
        'metadata|{}'.format(_("metadata")),
    ]

    # remove any instances of None
    while None in my_list: my_list.remove(None)

    return my_list


def get_review_field_list():
    my_list = [
        'collaboration_score_html|{}'.format("external pressures score"),
        'strategic_score_html|{}'.format("strategic direction score"),
        'operational_score_html|{}'.format("operational considerations score"),
        'ecological_score_html|{}'.format("ecological impact score"),
        'scale_score_html|{}'.format("scale score"),
        'total_score',
        'comments_for_staff',
        'approval_level',
        'approver_comment',
        'allocated_budget',
        'checklist_file',
        'metadata',
    ]
    return my_list


def get_staff_field_list():
    my_list = [
        'smart_name|{}'.format(_("name")),
        'funding_source',
        'is_primary_lead',
        'is_lead',
        'employee_type',
        'level',
        'duration_weeks',
        # 'overtime_hours',
        # 'overtime_description',
        # 'student_program',
        'amount',
        'allocated_amount',
    ]
    return my_list


def get_citation_field_list():
    my_list = [
        'tname|{}'.format(_("title")),
        'authors',
        'year',
        'publication',
        'pub_number',
        # 'turl|{}'.format(_("url")),
        'tabstract|{}'.format(_("abstract")),
        'series',
        'region',
    ]
    return my_list


def get_om_field_list():
    my_list = [
        'category_type|{}'.format(_("category type")),
        'om_category',
        'description',
        'funding_source',
        'amount',
        'allocated_amount',

    ]
    return my_list


def get_capital_field_list():
    my_list = [
        'category',
        'description',
        'funding_source',
        'amount',
        'allocated_amount',
    ]
    return my_list


def get_allocation_field_list():
    my_list = [
        'description',
        'funding_source',
        'amount',
        'distributed_amount',
    ]
    return my_list


def get_activity_field_list():
    my_list = [
        'type',
        'name',
        'description',
        'target_date',
        'responsible_party',
        'latest_update|{}'.format(_("latest status")),
    ]
    return my_list


def get_collaboration_field_list():
    my_list = [
        'type',
        'new_or_existing',
        'organization',
        'people',
        'critical',
        'agreement_title',
        # 'gc_program',
        # 'amount',
        'notes',
    ]
    return my_list


def get_status_report_field_list():
    my_list = [
        'report_number|{}'.format("number"),
        'status',
        'major_accomplishments_html|{}'.format(_("major accomplishments")),
        'major_issues_html|{}'.format(_("major issues")),
        'target_completion_date',
        'rationale_for_modified_completion_date',
        'excess_funds',
        'excess_funds_amt',
        'excess_funds_comment_html|{}'.format(_("suggested uses for remaining funds")),
        'insuficient_funds',
        'insuficient_funds_amt',
        'insuficient_funds_comment_html|{}'.format(_("additional funding requested description")),
        'general_comment',
        'supporting_resources|{}'.format(_("supporting resources")),
        'section_head_comment',
        'section_head_reviewed',
        'metadata',
    ]
    return my_list

def get_status_report_short_field_list():
    my_list = [
        'report_number|{}'.format("number"),
        'status',
        'target_completion_date',
        'excess_funds',
        'excess_funds_amt',
        'insuficient_funds',
        'insuficient_funds_amt',
        'general_comment',
        'supporting_resources|{}'.format(_("supporting resources")),
        'section_head_reviewed',
        'metadata',
    ]
    return my_list

def get_dma_field_list():
    my_list = [
        'title',
        'data_contact',
        'metadata_contact',
        'metadata_tool',
        'metadata_url',
        'metadata_update_freq',
        'metadata_freq_text',
        'storage_solutions',
        'storage_solution_text',
        'storage_needed',
        'raw_data_retention',
        'data_retention',
        'backup_plan',
        'cloud_costs',
        'had_sharing_agreements',
        'sharing_agreements_text',
        'publication_timeframe',
        'publishing_platforms',
        'comments',
        'status',
        'metadata',
    ]
    return my_list


def get_activity_update_field_list():
    my_list = [
        'activity',
        'status',
        'notes_html|{}'.format("notes"),
        'metadata|{}'.format("meta"),
    ]
    return my_list


def get_dma_review_field_list():
    my_list = [
        'fiscal_year',
        'decision',
        'comments',
        'metadata|{}'.format("metadata"),
    ]
    return my_list


def get_file_field_list():
    my_list = [
        'name',
        'ref|{}'.format("reference"),
        'external_url',
        'file',
        'date_created',

    ]
    return my_list


def get_review_score_rubric():
    return {
        "collaboration": {
            1: {
                "criteria": _(
                    "no formal commitments; limited interest from stakeholders; limited opportunity for partnership or collaboration."),
                "examples": _(
                    "No expressed interest or identified as a low priority (or potential conflict) by a stakeholder advisory committee."),
            },
            2: {
                "criteria": _("Informal departmental commitments; some interest from stakeholders; internal collaboration."),
                "examples": _(
                    "Verbal agreement with stakeholders or external partner. Collaboration between internal programs of science staff."),
            },
            3: {
                "criteria": _(
                    "regulatory or legal commitment; high interest from stakeholders; strong opportunity for external partnership and collaboration."),
                "examples": _("Signed G&C agreement with external partner."),
            },
        },
        "strategic": {
            1: {
                "criteria": _("limited long-term value; short-term benefit (fire-fighting)"),
                "examples": _(
                    "Local, archived dataset, with limited likelihood of replication going forward.   No clear link to decision-making."),
            },
            2: {
                "criteria": _("some strategic value to department; medium-term benefit"),
                "examples": _(
                    "Regional dataset of current high value, but potential to be replaced by emerging technology.  Indirect link to decision."),
            },
            3: {
                "criteria": _("high long-term strategic value to the department; high innovation value; broad applicability"),
                "examples": _(
                    "High value/priority, nationally consistent dataset using emerging, more cost effective (emerging) technology.  Clear link to high-priority decision-making."),
            },
        },
        "operational": {
            1: {
                "criteria": _("One-off project; feasible now but not sustainable in the long-term."),
                "examples": _("New data collection. Significant admin work required."),
            },
            2: {
                "criteria": _(
                    "Moderate level of feasibility or operational efficiency, e.g. equipment/tools readily available to be implemented within year"),
                "examples": _("Some processing/analysis required of an existing dataset."),
            },
            3: {
                "criteria": _(
                    "high feasibility, e.g. data availability, expertise, existing monitoring platforms, and regulatory tools available"),
                "examples": _(
                    "Open publication of an existing data layer.  Low administrative burden (e.g. existing agreements in place)."),
            },
        },
        "ecological": {
            1: {
                "criteria": _("limited ecological value, or lower priority species/habitats"),
                "examples": _("Project related to a species or area with limited or unknown ecological role, or of localized interest."),
            },
            2: {
                "criteria": _("Evidence of ecological value, e.g., prey linkages to key species."),
                "examples": _(
                    "Project related to a species or area with known linkages to a species of high ecological value (prey species), or importance identified through ecological modelling."),
            },
            3: {
                "criteria": _("high ecological value (important species) or high ecological risk (SARA-listed species)"),
                "examples": _(
                    "Project related to a nationally or regionally recognized ESS (Eelgrass) or EBSA (Minas Basin), or SAR (Blue Whale)."),
            },
        },
        "scale": {
            1: {
                "criteria": _("limited geographic or temporal scope; site-specific and lessons not readily applicable to other areas"),
                "examples": _("Data only available for a single location or bay."),
            },
            2: {
                "criteria": _("broad geographic/temporal scope; area of some significance"),
                "examples": _("Subregional data layer, e.g., for a single NAFO Unit or MPA."),
            },
            3: {
                "criteria": _("broad geographic or temporal scope; area of high significance"),
                "examples": _("Bioregional data layers, e.g. remote sensing, RV Survey."),
            },
        },

    }


def get_risk_rating(impact, likelihood):
    """This is taken from the ACRDP application form"""
    l = 1
    m = 2
    h = 3
    rating_dict = {
        # impact
        1: {
            # likelihood -- > risk rating
            1: l, 2: l, 3: l, 4: m, 5: m,
        },
        2: {
            1: l, 2: l, 3: m, 4: m, 5: m,
        },
        3: {
            1: l, 2: m, 3: m, 4: m, 5: h,
        },
        4: {
            1: m, 2: m, 3: m, 4: h, 5: h,
        },
        5: {
            1: m, 2: m, 3: h, 4: h, 5: h,
        },
    }
    return rating_dict[impact][likelihood]


def prime_csas_activities(project_year, starting_date, meeting_duration, has_sr_ar, has_res_or_proc):
    print(meeting_duration, starting_date)
    parent_activities = [
        dict(name="Planning", parent=None, type=1, description="Establishing steering committee, chair, science lead"),
        dict(name="Terms of Reference", parent=None, type=1, description="Meeting objective agreed upon by science sector and client"),
        dict(name="Peer-review Meeting", parent=None, type=1, description="Evaluation and consensus building"),
        dict(name="Science response or advisory report", parent=None, type=2, description="Timelines refer to document publication") if has_sr_ar else None,
        dict(name="Research document or proceedings", parent=None, type=2, description="Timelines refer to document publication") if has_res_or_proc else None,
    ]

    # first create all parents
    for a_dict in parent_activities:
        if a_dict:
            a = models.Activity.objects.create(
                project_year=project_year,
                name=a_dict["name"],
                type=a_dict["type"],
                description=a_dict["description"],
            )

    # Activities are the lead ups to the documents... these culminate in the `starting date`
    #
    #                  ___ child 1
    #  activities-----|                 [The fork is the starting datetime]
    #                  --- child 2

    activities = [
        # planning
        dict(duration=1, name="Pre-Meeting with Science Staff", parent="Planning", type=1,
             description="Identify science lead(s) and potential chair(s)"),
        dict(duration=30, name="Assemble Steering Committee", parent="Planning", type=1,
             description="Identify steering committee members: science leads, section head, CSAS advisor and clients"),

        # tor
        dict(duration=15, name="Complete ToR", parent="Terms of Reference", type=1, description="Complete ToR with steering committee"),
        dict(duration=14, name="ToR Approvals", parent="Terms of Reference", type=1,
             description="ToR approvals by client program and science director (or DG)"),
        dict(duration=10, name="Translate ToR", parent="Terms of Reference", type=1, description="Translate ToR"),
        dict(duration=28, name="Request to publish ToR", parent="Terms of Reference", type=1, description="Submit ToR through CSAS app"),

        # peer review
        dict(duration=42, name="Publish ToR (6 weeks prior to meeting)", parent="Peer-review Meeting", type=1,
             description="ToR to be posted on CSAS website 6 weeks prior to the meeting"),
        dict(duration=meeting_duration, name="Hold Meeting", parent="Peer-review Meeting", type=1, description="Evaluation and consensus building"),
    ]

    activities.reverse()  # we will start with the last activity and move back in time
    i = 0
    for a_dict in activities:
        if i == 0:
            end = starting_date  # finishes at the starting date
            start = starting_date - timedelta(days=meeting_duration)
        else:
            end = start
            start = end - timedelta(days=a_dict["duration"])

        a = models.Activity.objects.create(
            project_year=project_year,
            name=a_dict["name"],
            description=a_dict["description"],
            type=a_dict["type"],
            target_date=end,
            target_start_date=start,
        )
        if a_dict.get("parent"):
            parent = project_year.activities.get(name=a_dict["parent"])
            a.parent = parent
            a.save()
        i += 1

    # each activity begins at the starting datetime; they run in parallel
    child_activities = [
        # Science response or advisory report
        [
            dict(duration=28, name="Submit reworked documents", parent="Science response or advisory report", type=1,
                 description="To submit final document to regional CSAS office"),
            dict(duration=5, name="Management approval (1st language)", parent="Science response or advisory report", type=1,
                 description="Preliminary approval for translation"),
            dict(duration=45, name="Document translation", parent="Science response or advisory report", type=1, description="Send for translation"),
            dict(duration=21, name="Correct formatting (both languages)", parent="Science response or advisory report", type=1,
                 description="Document formatting by regional CSAS office"),
            dict(duration=5, name="Review and approval by authors", parent="Science response or advisory report", type=1,
                 description="Finalization and review of document formatting"),
            dict(duration=5, name="Final approvals by management", parent="Science response or advisory report", type=1,
                 description="Final approval for publication"),
            dict(duration=10, name="Send final documents to NCR", parent="Science response or advisory report", type=1,
                 description="Submit final documents for publication"),
        ] if has_sr_ar else None,

        # Research document or proceedings
        [
            dict(duration=60, name="Submit reworked meeting document(s)", parent="Research document or proceedings", type=1,
                 description="To submit final document to regional CSAS office"),
            dict(duration=5, name="Management approval (1st language)", parent="Research document or proceedings", type=1,
                 description="Preliminary approval for translation"),
            dict(duration=45, name="Document translation", parent="Research document or proceedings", type=1, description="Send for translation"),
            dict(duration=21, name="Correct formatting (both languages)", parent="Research document or proceedings", type=1,
                 description="Document formatting by regional CSAS office"),
            dict(duration=5, name="Review and approval by authors", parent="Research document or proceedings", type=1,
                 description="Finalization and review of document formatting"),
            dict(duration=5, name="Final approvals by management", parent="Research document or proceedings", type=1,
                 description="Final approval for publication"),
            dict(duration=5, name="Send final documents to NCR", parent="Research document or proceedings", type=1,
                 description="Submit final documents for publication"),
        ] if has_res_or_proc else None,
    ]

    for child_list in child_activities:
        if child_list:
            i = 0
            for a_dict in child_list:
                if i == 0:
                    start = starting_date  # starts at the starting date
                    end = starting_date + timedelta(days=a_dict["duration"])
                else:
                    start = end
                    end = start + timedelta(days=a_dict["duration"])

                a = models.Activity.objects.create(
                    project_year=project_year,
                    name=a_dict["name"],
                    description=a_dict["description"],
                    type=a_dict["type"],
                    target_date=end,
                    target_start_date=start,
                )

                if a_dict.get("parent"):
                    parent = project_year.activities.get(name=a_dict["parent"])
                    a.parent = parent
                    a.save()
                i += 1

    # now we have to figure out the dates of the parents
    for a_dict in parent_activities:
        if a_dict:
            a = models.Activity.objects.get(
                project_year=project_year,
                name=a_dict["name"],
                type=a_dict["type"],
            )
            children = a.children.order_by("target_start_date")
            start = children.first().target_start_date
            end = children.last().target_date
            a.target_start_date = start
            a.target_date = end
            a.save()


def get_project_year_queryset(request):
    qs = models.ProjectYear.objects.order_by("start_date")
    qp = request.query_params if hasattr(request, 'query_params') else request.GET

    if qp.get("ids"):
        ids = qp.get("ids").split(",")  # get project year list
        qs = qs.filter(id__in=ids)  # get project year qs
    else:
        filter_list = [
            "user",
            "is_hidden",
            "title",
            "id",
            'staff',
            'fiscal_year',
            'year',
            'tag',
            'theme',
            'functional_group',
            'funding_source',
            'region',
            'division',
            'section',
            'status',
            'field_component',
            'ship_component',
        ]
        for filter in filter_list:
            input = qp.get(filter)
            if input == "true":
                input = True
            elif input == "false":
                input = False
            elif input == "null" or input == "" or input == "None":
                input = None

            if input:
                if filter == "user":
                    qs = qs.filter(project__section__in=get_manageable_sections(request.user)).order_by("fiscal_year",
                                                                                                        "project_id")
                elif filter == "is_hidden":
                    qs = qs.filter(project__is_hidden=True)
                elif filter == "status":
                    qs = qs.filter(status=input)
                elif filter == "title":
                    qs = qs.filter(project__title__icontains=input)
                elif filter == "id":
                    qs = qs.filter(project__id=input)
                elif filter == "staff":
                    qs = qs.filter(project__staff_search_field__icontains=input)
                elif filter == "fiscal_year" or filter == "year":
                    qs = qs.filter(fiscal_year_id=input)
                elif filter == "tag":
                    qs = qs.filter(project__tags=input)
                elif filter == "theme":
                    qs = qs.filter(project__functional_group__theme_id=input)
                elif filter == "functional_group":
                    qs = qs.filter(project__functional_group_id=input)
                elif filter == "funding_source":
                    qs = qs.filter(project__default_funding_source_id=input)
                elif filter == "region":
                    qs = qs.filter(project__section__division__branch__region_id=input)
                elif filter == "division":
                    qs = qs.filter(project__section__division_id=input)
                elif filter == "section":
                    qs = qs.filter(project__section_id=input)
                elif filter == "field_component":
                    qs = qs.filter(has_field_component=True)
                elif filter == "ship_component":
                    qs = qs.filter(has_ship_needs=True)

        # if a regular user is making the request, show only approved projects (and not hidden projects)
        if not is_management_or_admin(request.user):
            qs = qs.filter(project__is_hidden=False, status__in=[2, 3, 4])
    return qs.distinct()


def get_staff_summary(staff_df, summary_type, summary_cols=None, na_value="---"):
    # Selects classified FTE week columns and performs a group by with the summary type column.
    if summary_cols is None:
        summary_cols = ['draft', 'submitted_unapproved', 'approved'] + [summary_type]
    output_summary = None
    if summary_type in staff_df.columns and not staff_df.empty:
        # sum FTE weeks based on type
        summary_df = staff_df.copy()
        summary_df = summary_df[summary_cols]
        summary_df.loc[:, summary_type] = summary_df[summary_type].fillna(value=na_value)
        summary_df = summary_df.groupby(summary_type).sum()

        # count occurences of summary type based off original df
        output_df = staff_df.copy()
        # hideous drop duplicates to make Nan's distinct
        output_df = output_df[(~output_df.duplicated(subset=['user', summary_type])) | (output_df[['user']].isnull().any(axis=1))]

        output_df.loc[:, summary_type] = output_df[summary_type].fillna(value=na_value)
        output_summary = pd.DataFrame(output_df[summary_type].value_counts())

        output_summary = output_summary.join(summary_df)
        output_summary = output_summary.fillna('')
        output_summary.rename(columns={summary_type: 'count'}, inplace=True)

        output_summary = output_summary.reset_index().to_dict('records')
    return output_summary
