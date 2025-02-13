import csv
import json
import os
from copy import deepcopy

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Value, TextField, Q
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _, gettext_lazy, get_language

from dm_apps.context_processor import my_envr
from lib.functions.custom_functions import fiscal_year
from lib.templatetags.custom_filters import nz
from shared_models import models as shared_models
from shared_models.views import CommonTemplateView, CommonCreateView, \
    CommonDetailView, CommonFilterView, CommonDeleteView, CommonUpdateView, CommonListView, CommonHardDeleteView, \
    CommonFormsetView, CommonFormView, CommonPopoutCreateView, CommonPopoutDeleteView, CommonPopoutUpdateView
from . import filters, forms, models, reports
from .mixins import CanModifyProjectRequiredMixin, AdminRequiredMixin, ManagerOrAdminRequiredMixin, \
    SuperuserOrNationalAdminRequiredMixin, PPTLoginRequiredMixin
from .utils import get_help_text_dict, \
    get_division_choices, get_section_choices, get_project_field_list, get_project_year_field_list, \
    is_management_or_admin, \
    get_review_score_rubric, get_status_report_field_list, get_review_field_list, get_user_fte_breakdown, \
    get_dma_field_list, get_dma_review_field_list, get_project_year_queryset, in_ppt_admin_group


class IndexTemplateView(PPTLoginRequiredMixin, CommonTemplateView):
    template_name = 'ppt/index.html'
    h1 = gettext_lazy("DFO Science Project Planning")
    active_page_name_crumb = gettext_lazy("Home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        section_id_list = []
        if self.request.user.id:
            if self.request.user.groups.filter(name="projects_admin").count() > 0:
                section_id_list = [project.section_id for project in models.Project.objects.all()]
                section_list = shared_models.Section.objects.filter(id__in=section_id_list)
            else:
                pass
        context["is_management_or_admin"] = is_management_or_admin(self.request.user)
        context["past_dates"] = models.UpcomingDate.objects.filter(date__lt=timezone.now()).order_by("date")
        context["upcoming_dates_field_list"] = [
            "date",
            "region",
            "tdescription|{}".format("description"),
        ]
        # project count
        project_ids = [staff.project_year.project_id for staff in self.request.user.staff_instances2.all()]
        project_count = models.Project.objects.filter(id__in=project_ids).order_by("-updated_at", "title").count()
        orphen_count = models.Project.objects.filter(years__isnull=True, modified_by=self.request.user).count()
        context["my_project_count"] = project_count + orphen_count

        upcoming_dates = models.UpcomingDate.objects.filter(date__gte=timezone.now()).order_by("date")
        context["upcoming_dates"] = upcoming_dates
        context["upcoming_dates_regions"] = [shared_models.Region.objects.get(pk=r["region"]) for r in
                                             upcoming_dates.order_by("region").values("region").distinct()]

        reference_materials = models.ReferenceMaterial.objects.all()
        context["reference_materials"] = models.ReferenceMaterial.objects.all()
        context["reference_materials_regions"] = [shared_models.Region.objects.get(pk=r["region"]) for r in
                                                  reference_materials.order_by("region").values("region").distinct()]

        return context

# HELPTEXT
class CommonCreateViewHelp(CommonCreateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['help_text_dict'] = get_help_text_dict(self.model)

        # if the UserMode table has this user in "edit" mode provide the
        # link to the dialog to manage help text via the manage_help_url
        # and provide the model name the help text will be assigned to.
        # The generic_form_with_help_text.html from the shared_models app
        # will provide the field name and together you have the required
        # model and field needed to make an entry in the Help Text table.
        if in_ppt_admin_group(self.request.user):
            if self.request.user.ppt_admin_user.mode == 2:
                context['manage_help_url'] = "ppt:manage_help_text"
                context['model_name'] = self.model.__name__
        return context


class CommonUpdateViewHelp(CommonUpdateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['help_text_dict'] = get_help_text_dict(self.model)
        # if the UserMode table has this user in "edit" mode provide the
        # link to the dialog to manage help text via the manage_help_url
        # and provide the model name the help text will be assigned to.
        # The generic_form_with_help_text.html from the shared_models app
        # will provide the field name and together you have the required
        # model and field needed to make an entry in the Help Text table.
        if in_ppt_admin_group(self.request.user):
            if self.request.user.ppt_admin_user.mode == 2:
                context['manage_help_url'] = "ppt:manage_help_text"
                context['model_name'] = self.model.__name__
        return context


# This is the dialog presented to the user to enter help text for a given model/field
# it uses the Create View to both create entries and update them. Accessed via the manage_help_url.
#
# A point of failure may be if the (model, field_name) pair is not unique in the help text table.
class HelpTextPopView(AdminRequiredMixin, CommonCreateView):
    model = models.HelpText
    form_class = forms.HelpTextPopForm
    success_url = reverse_lazy("shared_models:close_me")
    title = gettext_lazy("Update Help Text")

    def get_initial(self):
        if self.model.objects.filter(model=self.kwargs['model_name'], field_name=self.kwargs['field_name']):
            obj = self.model.objects.get(model=self.kwargs['model_name'], field_name=self.kwargs['field_name'])
            return {
                'model': self.kwargs['model_name'],
                'field_name': self.kwargs['field_name'],
                'eng_text': obj.eng_text,
                'fra_text': obj.fra_text
            }

        return {
            'model': self.kwargs['model_name'],
            'field_name': self.kwargs['field_name'],
        }

    def form_valid(self, form):
        if self.model.objects.filter(model=self.kwargs['model_name'], field_name=self.kwargs['field_name']):
            data = form.cleaned_data
            obj = self.model.objects.get(model=self.kwargs['model_name'], field_name=self.kwargs['field_name'])
            obj.eng_text = data['eng_text']
            obj.fra_text = data['fra_text']
            obj.save()
            return HttpResponseRedirect(reverse_lazy("shared_models:close_me"))
        else:
            return super().form_valid(form)


# PROJECTS #
############


class ExploreProjectsTemplateView(PPTLoginRequiredMixin, CommonTemplateView):
    h1 = gettext_lazy("Projects")
    template_name = 'ppt/explore_projects/main.html'
    home_url_name = "ppt:index"
    container_class = "container-fluid bg-light curvy"
    subtitle = gettext_lazy("Explore Projects")
    field_list = [
        'id',
        'title',
        'fiscal year',
        'status',
        # 'section',
        'default_funding_source',
        'functional_group',
        'lead_staff',
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["random_project"] = models.Project.objects.first()
        context["status_choices"] = [dict(label=item[1], value=item[0]) for item in models.ProjectYear.status_choices]
        context["activity_status_choices"] = [dict(label=f"{item[1]}", value=item[0]) for item in
                                              models.ActivityUpdate.status_choices]
        context["activity_type_choices"] = [dict(label=f"{item[1]}", value=item[0]) for item in
                                            models.Activity.type_choices]
        context["activity_classification_choices"] = [dict(label=f"{item.__str__()}", value=item.id) for item in
                                                      models.ActivityClassification.objects.all()]
        return context


class ManageProjectsTemplateView(ManagerOrAdminRequiredMixin, CommonTemplateView):
    h1 = gettext_lazy("Projects")
    template_name = 'ppt/manage_projects/main.html'
    home_url_name = "ppt:index"
    container_class = "container-fluid bg-light curvy"
    subtitle = gettext_lazy("Manage Projects")
    field_list = [
        'id',
        'fiscal year',
        'title',
        # 'section',
        'funding_sources_list',
        'functional_group',
        'lead_staff',
        'status',
        'review_score_percentage',
        'last_modified',
        'om_costs',
        'om_allocations',
        'salary_costs',
        'salary_allocations',
        'capital_costs',
        'capital_allocations',
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["random_project"] = models.Project.objects.first()
        context["status_choices"] = [dict(label=item[1], value=item[0]) for item in models.ProjectYear.status_choices]
        context["approval_status_choices"] = [dict(label=item[1], value=item[0]) for item in models.Review.approval_status_choices]
        context["approval_level_choices"] = [dict(label=item[1], value=item[0]) for item in models.Review.approval_level_choices]
        context["funding_status_choices"] = [dict(label=item[1], value=item[0]) for item in models.Review.funding_status_choices]
        context["om_cost_categories"] = [dict(label=f"{item.get_group_display()} - {item}", value=item.id) for item in models.OMCategory.objects.all()]
        context["activity_types"] = [dict(label=f"{item}", value=item.id) for item in models.ActivityType.objects.all()]
        context["status_report_status_choices"] = [dict(label=f"{item[1]}", value=item[0]) for item in models.StatusReport.status_choices]
        context["activity_status_choices"] = [dict(label=f"{item[1]}", value=item[0]) for item in models.ActivityUpdate.status_choices]
        context["activity_type_choices"] = [dict(label=f"{item[1]}", value=item[0]) for item in models.Activity.type_choices]
        context["activity_classification_choices"] = [dict(label=f"{item.__str__()}", value=item.id) for item in models.ActivityClassification.objects.all()]
        context["review_form"] = forms.ReviewForm
        context["approval_form"] = forms.ApprovalForm
        context["capital_allocation_form"] = forms.CapitalAllocationForm
        context["salary_allocation_form"] = forms.SalaryAllocationForm
        context["om_allocation_form"] = forms.OMAllocationForm
        context["review_score_rubric"] = json.dumps(get_review_score_rubric())
        context["short_field_list"] = [
            'id',
            'fiscal year',
            'title',
            'funding_sources_list',
            'status',
        ]
        return context


class MyProjectListView(PPTLoginRequiredMixin, CommonFilterView):
    template_name = 'ppt/my_project_list.html'
    filterset_class = filters.ProjectFilter
    h1 = gettext_lazy("My Projects")
    home_url_name = "ppt:index"
    container_class = "container-fluid bg-light curvy"
    row_object_url_name = "ppt:project_detail"
    new_object_url = reverse_lazy("ppt:project_new")
    field_list = [
        {"name": 'id', "class": "", "width": ""},
        {"name": 'section', "class": "", "width": ""},
        {"name": 'title', "class": "", "width": ""},
        {"name": 'start_date', "class": "", "width": "150px"},
        {"name": 'lead_staff', "class": "", "width": ""},
        {"name": 'fiscal_years_display|{}'.format(_("fiscal years")), "class": "", "width": ""},
        {"name": 'status', "class": "", "width": ""},
        {"name": 'has_unsubmitted_years|{}'.format("has unsubmitted years?"), "class": "", "width": ""},
        {"name": 'is_hidden|{}'.format(_("hidden?")), "class": "", "width": ""},
        {"name": 'updated_at', "class": "", "width": "150px"},
    ]

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        if kwargs["data"] is None:
            kwargs["data"] = {"fiscal_years": fiscal_year(timezone.now(), sap_style=True) + 1}
        return kwargs

    def get_queryset(self):
        project_ids = [staff.project_year.project_id for staff in self.request.user.staff_instances2.all()]
        return models.Project.objects.filter(id__in=project_ids).order_by("-updated_at", "title")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orphens = models.Project.objects.filter(years__isnull=True, modified_by=self.request.user)
        context["orphens"] = orphens
        status_dict = {}
        context["fiscal_year"] = ""
        fiscal_year = self.request.GET.get("fiscal_years")
        if fiscal_year:
            context["fiscal_year"] = shared_models.FiscalYear.objects.filter(pk=fiscal_year).get().__str__()
        qs = self.get_queryset()
        for proj in qs:
            status_dict[proj.id] = proj.year_status(fiscal_year)
        context["status_data"] = status_dict
        return context


class ProjectCreateView(PPTLoginRequiredMixin, CommonCreateViewHelp):
    model = models.Project
    form_class = forms.NewProjectForm
    home_url_name = "ppt:index"
    template_name = 'ppt/project_form.html'
    container_class = "container bg-light curvy"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['help_text_dict'] = get_help_text_dict()

        # here are the option objects we want to send in through context
        # only from the science branches of each region

        division_dict = {}
        for d in get_division_choices(all=True):
            my_division = shared_models.Division.objects.get(pk=d[0])
            division_dict[my_division.id] = {}
            division_dict[my_division.id]["display"] = "{} - {}".format(
                getattr(my_division.branch, _("name")),
                getattr(my_division, _("name")),
            )
            division_dict[my_division.id]["region_id"] = my_division.branch.region_id

        section_dict = {}
        for s in get_section_choices(all=True):
            my_section = shared_models.Section.objects.get(pk=s[0])
            section_dict[my_section.id] = {}
            section_dict[my_section.id]["display"] = str(my_section)
            section_dict[my_section.id]["division_id"] = my_section.division_id
        context['division_json'] = json.dumps(division_dict)
        context['section_json'] = json.dumps(section_dict)

        return context

    def form_valid(self, form):
        my_object = form.save(commit=False)
        # modifications to project instance before saving
        my_object.modified_by = self.request.user
        my_object.save()
        messages.success(self.request,
                         mark_safe(_(
                             "<span class='h4'>Your new project was created successfully! To get started, <b class='highlight'>add a new project year</b>.</span>")))
        return HttpResponseRedirect(reverse_lazy("ppt:project_detail", kwargs={"pk": my_object.id}))

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class ProjectDetailView(PPTLoginRequiredMixin, CommonDetailView):
    model = models.Project
    template_name = 'ppt/project_detail/main.html'
    home_url_name = "ppt:index"
    container_class = "container-fluid bg-light curvy"

    # parent_crumb = {"title": _("My Projects"), "url": reverse_lazy("ppt:my_project_list")}

    def get_active_page_name_crumb(self):
        return "{} {}".format(_("Project"), self.get_object().id)

    def get_h1(self):
        return self.get_object().title

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()

        # If this is a gulf region project, only show the gulf region fields
        context["project_field_list"] = get_project_field_list(project)
        context["project_year_field_list"] = get_project_year_field_list()

        context["random_review"] = models.Review.objects.first()
        context["review_field_list"] = get_review_field_list()

        context["staff_form"] = forms.StaffForm
        context["random_staff"] = models.Staff.objects.first()

        context["om_cost_form"] = forms.OMCostForm
        context["random_om_cost"] = models.OMCost.objects.first()

        context["capital_cost_form"] = forms.CapitalCostForm
        context["random_capital_cost"] = models.CapitalCost.objects.first()

        context["salary_allocation_form"] = forms.SalaryAllocationForm
        context["random_salary_allocation"] = models.SalaryAllocation.objects.first()

        context["om_allocation_form"] = forms.OMAllocationForm
        context["random_om_allocation"] = models.OMAllocation.objects.first()

        context["capital_allocation_form"] = forms.CapitalAllocationForm
        context["random_capital_allocation"] = models.CapitalAllocation.objects.first()

        context["activity_form"] = forms.ActivityForm(initial=dict(project=project))
        context["random_activity"] = models.Activity.objects.first()

        context["collaboration_form"] = forms.CollaborationForm
        context["random_collaboration"] = models.Collaboration.objects.first()

        context["status_report_form"] = forms.StatusReportForm(initial={"user": self.request.user}, instance=project)
        context["random_status_report"] = models.StatusReport.objects.first()

        context["file_form"] = forms.FileForm
        context["random_file"] = models.File.objects.first()

        context["btn_class_1"] = "create-btn"
        # context["files"] = project.files.all()
        # context["financial_summary_dict"] = financial_summary_data(project)

        # Determine if the user will be able to edit the project.
        # context["can_edit"] = can_modify_project(self.request.user, project.id)
        # context["is_lead"] = self.request.user in [staff.user for staff in project.staff_members.filter(lead=True)]
        return context


class ProjectUpdateView(CanModifyProjectRequiredMixin, CommonUpdateViewHelp):
    model = models.Project
    form_class = forms.ProjectForm
    template_name = 'ppt/project_form.html'
    home_url_name = "ppt:index"
    container_class = "container bg-light curvy"

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("ppt:project_detail", args=[self.get_object().id])}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['help_text_dict'] = get_help_text_dict()

        client_information_dict = {}
        for ci in models.CSRFClientInformation.objects.all().order_by("name", ):
            client_information_dict[ci.id] = {}
            client_information_dict[ci.id]["display"] = str(ci)
            if ci.fiscal_year:
                client_information_dict[ci.id]["fiscal_year"] = ci.fiscal_year.id
            else:
                client_information_dict[ci.id]["fiscal_year"] = None

        context['client_information_json'] = json.dumps(client_information_dict)

        return context

    def get_initial(self):
        return dict(modified_by=self.request.user)


class ProjectDeleteView(CanModifyProjectRequiredMixin, CommonDeleteView):
    model = models.Project
    delete_protection = False
    home_url_name = "ppt:index"
    success_url = reverse_lazy("ppt:index")
    template_name = "ppt/confirm_delete.html"
    container_class = "container bg-light curvy"

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("ppt:project_detail", args=[self.get_object().id])}


class ProjectCloneView(ProjectUpdateView):
    template_name = 'ppt/project_form.html'

    def get_h1(self):
        return _("Cloning: ") + str(self.get_object())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cloning"] = True
        return context

    def test_func(self):
        return self.request.user.is_authenticated

    def get_initial(self):
        obj = self.get_object()
        init = super().get_initial()
        init["title"] = f"CLONE OF: {obj.title}"
        init["cloning"] = True
        return init

    def form_valid(self, form):
        new_obj = form.save(commit=False)
        old_obj = models.Project.objects.get(pk=new_obj.pk)

        new_obj.project = new_obj
        new_obj.pk = None
        new_obj.save()

        for t in old_obj.tags.all():
            new_obj.tags.add(t)

        # for each year of old project, clone into new project...
        for old_year in old_obj.years.all():
            new_year = deepcopy(old_year)

            new_year.project = new_obj
            new_year.pk = None
            new_year.submitted = None
            new_year.status = 1
            new_year.approval_notification_email_sent = None
            new_year.save()

            # Now we need to replicate all the related records:
            # 1) staff
            for old_rel_obj in old_year.staff_set.all():
                new_rel_obj = deepcopy(old_rel_obj)
                new_rel_obj.pk = None
                new_rel_obj.project_year = new_year
                new_rel_obj.save()

            # we have to just make sure that the user is a lead on the project. Otherwise they will not be able to edit.
            my_staff, created = models.Staff.objects.get_or_create(
                user=self.request.user,
                project_year=new_year,
                employee_type_id=1,
            )
            my_staff.lead = True
            my_staff.save()

            # 2) O&M
            for old_rel_obj in old_year.omcost_set.all():
                new_rel_obj = deepcopy(old_rel_obj)
                new_rel_obj.pk = None
                new_rel_obj.project_year = new_year
                new_rel_obj.save()

            # 3) Capital
            for old_rel_obj in old_year.capitalcost_set.all():
                new_rel_obj = deepcopy(old_rel_obj)
                new_rel_obj.pk = None
                new_rel_obj.project_year = new_year
                new_rel_obj.save()

            # 5) Collaborations
            for old_rel_obj in old_year.collaborations.all():
                new_rel_obj = deepcopy(old_rel_obj)
                new_rel_obj.pk = None
                new_rel_obj.project_year = new_year
                new_rel_obj.save()

            # 7) Activities
            for old_rel_obj in old_year.activities.all():
                new_rel_obj = deepcopy(old_rel_obj)
                new_rel_obj.pk = None
                new_rel_obj.project_year = new_year
                new_rel_obj.target_date = None  # clear the target date
                new_rel_obj.save()

        return HttpResponseRedirect(reverse_lazy("ppt:project_detail", kwargs={"pk": new_obj.project.id}))


class ProjectReferencesDetailView(PPTLoginRequiredMixin, CommonDetailView):
    model = models.Project
    template_name = 'ppt/project_references.html'
    home_url_name = "ppt:index"
    container_class = "container-fluid bg-light curvy"
    h1 = gettext_lazy("Project References")
    active_page_name_crumb = gettext_lazy("Project References")

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("ppt:project_detail", args=[self.get_object().id])}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["citation_form"] = forms.CitationForm
        context["random_citation"] = shared_models.Citation.objects.first()
        return context


# PROJECT YEAR #
################


class ProjectYearCreateView(CanModifyProjectRequiredMixin, CommonCreateViewHelp):
    model = models.ProjectYear
    form_class = forms.ProjectYearForm
    home_url_name = "ppt:index"
    template_name = 'ppt/project_year_form.html'
    container_class = "container bg-light curvy"

    def get_initial(self):
        # this is an important method to keep since it is accessed by the Form class
        # TODO: TEST ME
        return dict(project=self.get_project())

    def get_project(self):
        return models.Project.objects.get(pk=self.kwargs["project"])

    def get_parent_crumb(self):
        return {"title": self.get_project(), "url": reverse_lazy("ppt:project_detail", args=[self.get_project().id])}

    def form_valid(self, form):
        year = form.save(commit=False)
        year.modified_by = self.request.user
        year.save()

        # for good measure, we should add the current user as a staff to this year
        models.Staff.objects.create(
            project_year=year,
            user=self.request.user,
            employee_type=models.EmployeeType.objects.get(pk=1),
            is_lead=True,
        )

        return HttpResponseRedirect(
            super().get_success_url() + f"?project_year={year.id}"
        )


class ProjectYearUpdateView(CanModifyProjectRequiredMixin, CommonUpdateViewHelp):
    model = models.ProjectYear
    form_class = forms.ProjectYearForm
    home_url_name = "ppt:index"
    template_name = 'ppt/project_year_form.html'
    container_class = "container bg-light curvy"

    def get_h1(self):
        return _("Edit ") + str(self.get_object())

    def get_project(self):
        return self.get_object().project

    def get_parent_crumb(self):
        return {"title": self.get_project(), "url": reverse_lazy("ppt:project_detail", args=[self.get_project().id])}

    def form_valid(self, form):
        year = form.save(commit=False)
        year.modified_by = self.request.user
        year.save()
        return super().form_valid(form)

    def get_success_url(self):
        return super().get_success_url() + f"?project_year={self.get_object().id}"


class ProjectYearGanttDetailView(PPTLoginRequiredMixin, CommonDetailView):
    model = models.ProjectYear
    home_url_name = "ppt:index"
    template_name = 'ppt/project_year_gantt.html'
    container_class = "container-fluid"

    def get_h1(self):
        return _("Gantt Chart for Project ") + str(self.get_project().id)

    def get_project(self):
        return self.get_object().project

    def get_parent_crumb(self):
        return {"title": self.get_project(), "url": reverse_lazy("ppt:project_detail", args=[self.get_project().id])}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self.get_project()
        return context


class ProjectYearDeleteView(CanModifyProjectRequiredMixin, CommonDeleteView):
    model = models.ProjectYear
    delete_protection = False
    home_url_name = "ppt:index"
    template_name = "ppt/confirm_delete.html"
    container_class = "container bg-light curvy"

    def get_grandparent_crumb(self):
        return {"title": self.get_project(), "url": reverse("ppt:project_detail", args=[self.get_project().id])}

    def get_project(self):
        return self.get_object().project

    def delete(self, request, *args, **kwargs):
        project = self.get_project()
        self.get_object().delete()
        project.save()
        return HttpResponseRedirect(reverse("ppt:project_detail", args=[project.id]))


class ProjectYearCloneView(ProjectYearUpdateView):
    template_name = 'ppt/project_year_form.html'

    def get_h1(self):
        return _("Cloning: ") + str(self.get_object())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cloning"] = True
        return context

    def test_func(self):
        return self.request.user.is_authenticated

    def get_initial(self):
        init = super().get_initial()
        init["start_date"] = timezone.now()
        init["cloning"] = True
        return init

    def form_valid(self, form):
        new_obj = form.save(commit=False)
        old_obj = models.ProjectYear.objects.get(pk=new_obj.pk)

        new_obj.pk = None
        new_obj.submitted = None
        new_obj.status = 1
        new_obj.approval_notification_email_sent = None
        new_obj.save()

        # Now we need to replicate all the related records:
        # 1) staff
        for old_rel_obj in old_obj.staff_set.all():
            new_rel_obj = deepcopy(old_rel_obj)
            new_rel_obj.pk = None
            new_rel_obj.project_year = new_obj
            new_rel_obj.save()

        # we have to just make sure that the user is a lead on the project. Otherwise they will not be able to edit.
        # but, there is a chance (and likely probability) that they will already be on there.
        try:
            my_staff, created = models.Staff.objects.get_or_create(
                user=self.request.user,
                project_year=new_obj,
                employee_type_id=1,
            )
            my_staff.lead = True
            my_staff.save()
        except IntegrityError:
            pass

        # 2) O&M
        for old_rel_obj in old_obj.omcost_set.all():
            new_rel_obj = deepcopy(old_rel_obj)
            new_rel_obj.pk = None
            new_rel_obj.project_year = new_obj
            new_rel_obj.save()

        # 3) Capital
        for old_rel_obj in old_obj.capitalcost_set.all():
            new_rel_obj = deepcopy(old_rel_obj)
            new_rel_obj.pk = None
            new_rel_obj.project_year = new_obj
            new_rel_obj.save()

        # 5) Collaborations
        for old_rel_obj in old_obj.collaborations.all():
            new_rel_obj = deepcopy(old_rel_obj)
            new_rel_obj.pk = None
            new_rel_obj.project_year = new_obj
            new_rel_obj.save()

        # 7) Activities
        for old_rel_obj in old_obj.activities.all():
            new_rel_obj = deepcopy(old_rel_obj)
            new_rel_obj.pk = None
            new_rel_obj.project_year = new_obj
            new_rel_obj.target_date = None  # clear the target date
            new_rel_obj.save()

        return HttpResponseRedirect(reverse_lazy("ppt:project_detail", kwargs={"pk": new_obj.project.id}))


# FUNCTIONAL GROUPS #
#####################

class FunctionalGroupListView(AdminRequiredMixin, CommonFilterView):
    template_name = 'ppt/list.html'
    filterset_class = filters.FunctionalGroupFilter
    home_url_name = "ppt:index"
    new_object_url = reverse_lazy("ppt:group_new")
    row_object_url_name = row_ = "ppt:group_edit"
    container_class = "container-fluid bg-light curvy"

    field_list = [
        {"name": 'tname|{}'.format("name"), "class": "", "width": ""},
        {"name": 'theme', "class": "", "width": ""},
        {"name": 'sections', "class": "", "width": "600px"},
    ]

    def get_queryset(self):
        return models.FunctionalGroup.objects.annotate(
            search_term=Concat('name', Value(" "), 'nom', Value(" "), output_field=TextField()))


class FunctionalGroupUpdateView(AdminRequiredMixin, CommonUpdateViewHelp):
    model = models.FunctionalGroup
    form_class = forms.FunctionalGroupForm
    template_name = 'ppt/form.html'
    home_url_name = "ppt:index"
    parent_crumb = {"title": gettext_lazy("Functional Groups"), "url": reverse_lazy("ppt:group_list")}
    container_class = "container bg-light curvy"


class FunctionalGroupCreateView(AdminRequiredMixin, CommonCreateViewHelp):
    model = models.FunctionalGroup
    form_class = forms.FunctionalGroupForm
    success_url = reverse_lazy('ppt:group_list')
    template_name = 'ppt/form.html'
    home_url_name = "ppt:index"
    parent_crumb = {"title": gettext_lazy("Functional Groups"), "url": reverse_lazy("ppt:group_list")}
    container_class = "container bg-light curvy"


class FunctionalGroupDeleteView(AdminRequiredMixin, CommonDeleteView):
    model = models.FunctionalGroup
    success_url = reverse_lazy('ppt:group_list')
    success_message = 'The functional group was successfully deleted!'
    template_name = 'ppt/confirm_delete.html'
    container_class = "container bg-light curvy"


# SETTINGS #
############
class FundingSourceHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = models.FundingSource
    success_url = reverse_lazy("ppt:manage_funding_sources")


class FundingSourceFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'ppt/formset.html'
    h1 = "Manage Funding Source"
    queryset = models.FundingSource.objects.all()
    formset_class = forms.FundingSourceFormset
    success_url = reverse_lazy("ppt:manage_funding_sources")
    home_url_name = "ppt:index"
    delete_url_name = "ppt:delete_funding_source"
    container_class = "container bg-light curvy"


class OMCategoryHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = models.OMCategory
    success_url = reverse_lazy("ppt:manage_om_cats")


class OMCategoryFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'ppt/formset.html'
    h1 = "Manage OMCategory"
    queryset = models.OMCategory.objects.all()
    formset_class = forms.OMCategoryFormset
    success_url = reverse_lazy("ppt:manage_om_cats")
    home_url_name = "ppt:index"
    delete_url_name = "ppt:delete_om_cat"
    container_class = "container bg-light curvy"


class EmployeeTypeHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = models.EmployeeType
    success_url = reverse_lazy("ppt:manage_employee_types")


class EmployeeTypeFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'ppt/formset.html'
    h1 = "Manage Employee Type"
    queryset = models.EmployeeType.objects.all()
    formset_class = forms.EmployeeTypeFormset
    success_url = reverse_lazy("ppt:manage_employee_types")
    home_url_name = "ppt:index"
    delete_url_name = "ppt:delete_employee_type"
    container_class = "container bg-light curvy"


class TagHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = models.Tag
    success_url = reverse_lazy("ppt:manage_tags")


class TagFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'ppt/formset.html'
    h1 = "Manage Tag"
    queryset = models.Tag.objects.all()
    formset_class = forms.TagFormset
    success_url = reverse_lazy("ppt:manage_tags")
    home_url_name = "ppt:index"
    delete_url_name = "ppt:delete_tag"
    container_class = "container bg-light curvy"


class HelpTextHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = models.HelpText
    success_url = reverse_lazy("ppt:manage_help_texts")


class HelpTextFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'ppt/helptext_formset.html'
    h1 = "Manage Help Text"
    queryset = models.HelpText.objects.all()
    formset_class = forms.HelpTextFormset
    success_url = reverse_lazy("ppt:manage_help_texts")
    home_url_name = "ppt:index"
    delete_url_name = "ppt:delete_help_text"
    container_class = "container bg-light curvy"


class LevelHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = models.Level
    success_url = reverse_lazy("ppt:manage_levels")


class LevelFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'ppt/formset.html'
    h1 = "Manage Level"
    queryset = models.Level.objects.all()
    formset_class = forms.LevelFormset
    success_url = reverse_lazy("ppt:manage_levels")
    home_url_name = "ppt:index"
    delete_url_name = "ppt:delete_level"
    container_class = "container bg-light curvy"


class ActivityTypeHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = models.ActivityType
    success_url = reverse_lazy("ppt:manage_activity_types")


class ActivityTypeFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'ppt/formset.html'
    h1 = "Manage Activity Type"
    queryset = models.ActivityType.objects.all()
    formset_class = forms.ActivityTypeFormset
    success_url = reverse_lazy("ppt:manage_activity_types")
    home_url_name = "ppt:index"
    delete_url_name = "ppt:delete_activity_type"
    container_class = "container bg-light curvy"

class ActivityClassificationHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = models.ActivityClassification
    success_url = reverse_lazy("ppt:manage_activity_classifications")


class ActivityClassificationFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'ppt/formset.html'
    h1 = "Manage Activity Classifications"
    queryset = models.ActivityClassification.objects.all()
    formset_class = forms.ActivityClassificationFormset
    success_url = reverse_lazy("ppt:manage_activity_classifications")
    home_url_name = "ppt:index"
    delete_url_name = "ppt:delete_activity_classification"
    container_class = "container bg-light curvy"


class ThemeHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = models.Theme
    success_url = reverse_lazy("ppt:manage_themes")


class ThemeFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'ppt/formset.html'
    h1 = "Manage Theme"
    queryset = models.Theme.objects.all()
    formset_class = forms.ThemeFormset
    success_url = reverse_lazy("ppt:manage_themes")
    home_url_name = "ppt:index"
    delete_url_name = "ppt:delete_theme"
    container_class = "container bg-light curvy"


class UpcomingDateHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = models.UpcomingDate
    success_url = reverse_lazy("ppt:manage-upcoming-dates")


class UpcomingDateFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'ppt/formset.html'
    h1 = "Manage Upcoming Dates"
    queryset = models.UpcomingDate.objects.all()
    formset_class = forms.UpcomingDateFormset
    success_url = reverse_lazy("ppt:manage-upcoming-dates")
    home_url_name = "ppt:index"
    delete_url_name = "ppt:delete-upcoming-date"
    container_class = "container bg-light curvy"


class CSRFThemeFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'ppt/formset.html'
    h1 = "Manage CSRF Themes"
    queryset = models.CSRFTheme.objects.all()
    formset_class = forms.CSRFThemeFormset
    success_url_name = "ppt:manage_csrf_themes"
    home_url_name = "ppt:index"
    delete_url_name = "ppt:delete_csrf_theme"
    container_class = "container bg-light curvy"


class CSRFThemeHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = models.CSRFTheme
    success_url = reverse_lazy("ppt:manage_csrf_themes")


class CSRFSubThemeFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'ppt/formset.html'
    h1 = "Manage CSRF Sub Themes"
    queryset = models.CSRFSubTheme.objects.all()
    formset_class = forms.CSRFSubThemeFormset
    success_url_name = "ppt:manage_csrf_sub_themes"
    home_url_name = "ppt:index"
    delete_url_name = "ppt:delete_csrf_sub_theme"
    container_class = "container bg-light curvy"


class CSRFSubThemeHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = models.CSRFSubTheme
    success_url = reverse_lazy("ppt:manage_csrf_sub_themes")


class CSRFPriorityFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'ppt/formset.html'
    h1 = "Manage CSRF Priorities"
    queryset = models.CSRFPriority.objects.all()
    formset_class = forms.CSRFPriorityFormset
    success_url_name = "ppt:manage_csrf_priorities"
    home_url_name = "ppt:index"
    delete_url_name = "ppt:delete_csrf_priority"
    container_class = "container bg-light curvy"


class CSRFPriorityHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = models.CSRFPriority
    success_url = reverse_lazy("ppt:manage_csrf_priorities")


class CSRFClientInformationFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'ppt/formset.html'
    h1 = "Manage CSRF Client Information"
    queryset = models.CSRFClientInformation.objects.all()
    formset_class = forms.CSRFClientInformationFormset
    success_url_name = "ppt:manage_csrf_client_information"
    home_url_name = "ppt:index"
    delete_url_name = "ppt:delete_csrf_client_information"
    container_class = "container-fluid bg-light curvy"


class CSRFClientInformationHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = models.CSRFClientInformation
    success_url = reverse_lazy("ppt:manage_csrf_client_information")


class ServiceFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'ppt/formset.html'
    h1 = "Manage Services"
    queryset = models.Service.objects.all()
    formset_class = forms.ServiceFormset
    success_url_name = "ppt:manage_services"
    home_url_name = "ppt:index"
    delete_url_name = "ppt:delete_service"
    container_class = "container-fluid bg-light curvy"


class ServiceHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = models.Service
    success_url = reverse_lazy("ppt:manage_services")


class PPTAdminUserFormsetView(SuperuserOrNationalAdminRequiredMixin, CommonFormsetView):
    template_name = 'ppt/formset.html'
    h1 = "Manage PPT Administrative Users"
    queryset = models.PPTAdminUser.objects.all()
    formset_class = forms.PPTAdminUserFormset
    success_url_name = "ppt:manage_ppt_admin_users"
    home_url_name = "ppt:index"
    delete_url_name = "ppt:delete_ppt_admin_user"
    container_class = "container bg-light curvy"


class PPTAdminUserHardDeleteView(SuperuserOrNationalAdminRequiredMixin, CommonHardDeleteView):
    model = models.PPTAdminUser
    success_url = reverse_lazy("ppt:manage_ppt_admin_users")


class StorageSolutionFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'ppt/formset.html'
    h1 = "Manage Storage Solutions"
    queryset = models.StorageSolution.objects.all()
    formset_class = forms.StorageSolutionFormset
    success_url_name = "ppt:manage_storage_solutions"
    home_url_name = "ppt:index"
    delete_url_name = "ppt:delete_storage_solution"
    container_class = "container bg-light curvy"


class StorageSolutionHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = models.StorageSolution
    success_url = reverse_lazy("ppt:manage_storage_solutions")


# Reference Materials
class ReferenceMaterialListView(AdminRequiredMixin, CommonListView):
    template_name = "ppt/list.html"
    model = models.ReferenceMaterial
    field_list = [
        {"name": "tname|{}".format(gettext_lazy("name")), "class": "", "width": ""},
        {"name": "region", "class": "", "width": ""},
        {"name": "file_display_en|{}".format(gettext_lazy("File attachment (EN)")), "class": "", "width": ""},
        {"name": "file_display_fr|{}".format(gettext_lazy("File attachment (FR)")), "class": "", "width": ""},
        {"name": "date_created", "class": "", "width": ""},
        {"name": "date_modified", "class": "", "width": ""},
    ]
    new_object_url_name = "ppt:ref_mat_new"
    row_object_url_name = "ppt:ref_mat_edit"
    home_url_name = "ppt:index"
    h1 = gettext_lazy("Reference Materials")
    container_class = "container bg-light curvy"


class ReferenceMaterialUpdateView(AdminRequiredMixin, CommonUpdateViewHelp):
    model = models.ReferenceMaterial
    form_class = forms.ReferenceMaterialForm
    home_url_name = "ppt:index"
    parent_crumb = {"title": _("Reference Materials"), "url": reverse_lazy("ppt:ref_mat_list")}
    template_name = "ppt/form.html"
    is_multipart_form_data = True
    container_class = "container bg-light curvy"

    def get_delete_url(self):
        return reverse("ppt:ref_mat_delete", args=[self.get_object().id])


class ReferenceMaterialCreateView(AdminRequiredMixin, CommonCreateViewHelp):
    model = models.ReferenceMaterial
    form_class = forms.ReferenceMaterialForm
    home_url_name = "ppt:index"
    parent_crumb = {"title": _("Reference Materials"), "url": reverse_lazy("ppt:ref_mat_list")}
    template_name = "ppt/form.html"
    is_multipart_form_data = True
    container_class = "container bg-light curvy"


class ReferenceMaterialDeleteView(AdminRequiredMixin, CommonDeleteView):
    model = models.ReferenceMaterial
    success_url = reverse_lazy('ppt:ref_mat_list')
    home_url_name = "ppt:index"
    parent_crumb = {"title": _("Reference Materials"), "url": reverse_lazy("ppt:ref_mat_list")}
    template_name = "ppt/confirm_delete.html"
    delete_protection = False
    container_class = "container bg-light curvy"


# ADMIN


class AdminStaffListView(AdminRequiredMixin, CommonFilterView):
    template_name = 'ppt/admin_staff_list.html'

    filterset_class = filters.StaffFilter
    home_url_name = "ppt:index"
    h1 = gettext_lazy("Non-DMApps Staff List")
    h2 = gettext_lazy(
        "The purpose of this list view is to check if any DFO staff were listed on projects, but were not connected to their dmapps user accounts")
    field_list = [
        {"name": 'project_year.fiscal_year', "class": "", "width": ""},
        {"name": 'smart_name|staff name', "class": "", "width": ""},
        {"name": 'is_lead', "class": "", "width": ""},
        {"name": 'employee_type', "class": "", "width": ""},
    ]
    row_object_url_name = "ppt:admin_staff_edit"

    def get_queryset(self):
        qs = models.Staff.objects.filter(user__isnull=True, name__isnull=False).filter(
            ~Q(name__icontains="unknown")).filter(~Q(name__icontains="tbd")).filter(
            ~Q(name__icontains="BI-")).filter(~Q(name__icontains="PC-")).filter(~Q(name__icontains="EG-")).filter(
            ~Q(name__icontains="determined")).filter(
            ~Q(name__icontains="to be")).filter(~Q(name__icontains="student")).filter(
            ~Q(name__icontains="casual")).filter(
            ~Q(name__icontains="technician")).filter(~Q(name__icontains="crew")).filter(
            ~Q(name__icontains="hired")).filter(
            ~Q(name__icontains="support")).filter(~Q(name__icontains="volunteer")).filter(
            ~Q(name__icontains="staff")).filter(~Q(name__icontains="tba")).filter(
            ~Q(name__icontains="1")).filter(~Q(name__icontains="2")).filter(~Q(name__icontains="3"))

        qs = qs.order_by('name')
        return qs


class AdminStaffUpdateView(AdminRequiredMixin, CommonUpdateViewHelp):
    '''This is really just for the admin view'''
    model = models.Staff
    template_name = 'ppt/admin_staff_form.html'
    form_class = forms.AdminStaffForm
    h1 = gettext_lazy("Edit Non-DMApps Staff Member")
    parent_crumb = {"title": _("Non-registered Staff List"), "url": reverse_lazy("ppt:admin_staff_list")}
    container_class = "container bg-light curvy"

    def form_valid(self, form):
        obj = form.save()
        success_url = reverse("ppt:admin_staff_list")
        if self.request.META["QUERY_STRING"]:
            success_url += f"?{self.request.META['QUERY_STRING']}"

        # look for other matches:
        if obj.user and obj.user.first_name and obj.user.last_name:
            search_name = f"{obj.user.first_name} {obj.user.last_name}"
            qs = models.Staff.objects.filter(name__contains=search_name)

            messages.info(self.request,
                          f"Searched, found and replaced {qs.count()} additional matches for '{search_name}'")
            for staff in qs.all():
                staff.user = obj.user
                staff.save()

        return HttpResponseRedirect(success_url)

    def get_initial(self):
        name = self.get_object().name
        first = name.split(" ")[0]
        last = name.split(" ")[1]
        qs = User.objects.filter(first_name__icontains=first, last_name__icontains=last)
        if qs.exists() and qs.count() == 1:
            return dict(user=qs.first().id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['help_text_dict'] = get_help_text_dict()
        name = self.get_object().name
        first = name.split(" ")[0]
        last = name.split(" ")[1]
        context['name_count'] = models.Staff.objects.filter(name=name).count()
        context['match_found'] = User.objects.filter(first_name__icontains=first, last_name__icontains=last).exists()

        return context


# STATUS REPORT #
#################


class StatusReportDeleteView(CanModifyProjectRequiredMixin, CommonDeleteView):
    template_name = "ppt/confirm_delete.html"
    model = models.StatusReport
    container_class = "container bg-light curvy"
    delete_protection = False

    def get_project_year(self):
        return self.get_object().project_year

    def get_success_url(self, **kwargs):
        return reverse_lazy("shared_models:close_me")

    def get_parent_crumb(self):
        return {"title": str(self.get_object()), "url": reverse_lazy("ppt:report_detail", args=[self.get_object().id])}

    def get_grandparent_crumb(self):
        return {"title": str(self.get_project_year().project), "url": reverse_lazy("ppt:project_detail", args=[
            self.get_project_year().project.id]) + f"?project_year={self.get_project_year().id}"}


class StatusReportDetailView(PPTLoginRequiredMixin, CommonDetailView):
    model = models.StatusReport
    home_url_name = "ppt:index"
    template_name = "ppt/status_report/main.html"
    field_list = get_status_report_field_list()

    def dispatch(self, request, *args, **kwargs):
        # when the view loads, let's make sure that all the activities are on the project.
        my_object = self.get_object()
        my_project_year = my_object.project_year
        for activity in my_project_year.activities.all():
            my_update, created = models.ActivityUpdate.objects.get_or_create(
                activity=activity,
                status_report=my_object
            )
            # if the update is being created, what should be the starting status?
            # to know, we would have to look and see if there is another report. if there is, we should grab the penultimate report and copy status from there.
            if created:
                # check to see if there is another update on the same activity. We can do this since activities are unique to projects.
                if activity.updates.count() > 1:
                    # if there are more than just 1 (i.e. the one we just created), it will be the second record we are interested in...
                    last_update = activity.updates.all()[1]
                    my_update.status = last_update.status
                    my_update.save()

        return super().dispatch(request, *args, **kwargs)

    def get_project_year(self):
        return self.get_object().project_year

    def get_parent_crumb(self):
        return {"title": str(self.get_project_year().project), "url": reverse_lazy("ppt:project_detail", args=[
            self.get_project_year().project.id]) + f"?project_year={self.get_project_year().id}"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_report = self.get_object()
        context['files'] = my_report.files.all()
        context['file_form'] = forms.FileForm
        context["random_file"] = models.File.objects.first()
        context['update_form'] = forms.ActivityUpdateForm
        context["random_update"] = models.ActivityUpdate.objects.first()

        return context


class StatusReportUpdateView(CanModifyProjectRequiredMixin, CommonUpdateViewHelp):
    model = models.StatusReport
    form_class = forms.StatusReportForm
    home_url_name = "ppt:index"
    parent_crumb = {"title": _("Reference Materials"), "url": reverse_lazy("ppt:report_list")}
    template_name = "ppt/form.html"
    is_multipart_form_data = True
    container_class = "container bg-light curvy"

    def get_project_year(self):
        return self.get_object().project_year

    def get_parent_crumb(self):
        return {"title": str(self.get_object()), "url": reverse_lazy("ppt:report_detail", args=[self.get_object().id])}

    def get_grandparent_crumb(self):
        return {"title": str(self.get_project_year().project), "url": reverse_lazy("ppt:project_detail", args=[
            self.get_project_year().project.id]) + f"?project_year={self.get_project_year().id}"}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.modified_by = self.request.user
        obj.save()
        return super().form_valid(form)


class StatusReportReviewUpdateView(ManagerOrAdminRequiredMixin, StatusReportUpdateView):
    form_class = forms.StatusReportReviewForm
    h1 = gettext_lazy("Please provide review comments")
    container_class = "container bg-light curvy"


class StatusReportPrintDetailView(PPTLoginRequiredMixin, CommonDetailView):
    template_name = "ppt/status_report_pdf.html"
    model = models.StatusReport

    def get_h2(self):
        return f'{self.get_project_year().project} ({self.get_project_year()})'

    def get_project_year(self):
        return self.get_object().project_year

    def get_parent_crumb(self):
        return {"title": str(self.get_project_year().project), "url": reverse_lazy("ppt:project_detail", args=[
            self.get_project_year().project.id]) + f"?project_year={self.get_project_year().id}"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_report = get_object_or_404(models.StatusReport, pk=self.kwargs["pk"])
        context["object"] = my_report

        context["random_file"] = models.File.objects.first()
        context["random_update"] = models.ActivityUpdate.objects.first()

        return context



# REPORTS #
###########


class ManagementReportSearchFormView(AdminRequiredMixin, CommonFormView):
    template_name = 'ppt/management_search.html'
    form_class = forms.ManagementSearchForm
    h1 = gettext_lazy("Project Planning Reports")
    success_url = reverse_lazy("shared_models:close_me")

    def form_valid(self, form):
        report = int(form.cleaned_data["report"])

        # responce = generate_project_status_summary(self)
        if report == 1:
            return culture_committee_report(self.request)
        elif report == 2:
            return export_csrf_submission_list(self.request)
        elif report == 3:
            return project_status_summary(self.request)
        elif report == 4:
            return export_project_list(self.request)
        elif report == 5:
            return export_sar_workplan(self.request)
        elif report == 6:
            return export_regional_staff_allocation(self.request)
        elif report == 7:
            return export_project_position_allocation(self.request)
        elif report == 8:
            return export_capital_request_costs(self.request)
        elif report == 9:
            return export_project_summary(self.request)
        else:
            messages.error(self.request, "Report is not available. Please select another report.")
            return HttpResponseRedirect(reverse("ppt:reports"))


class ReportSearchFormView(AdminRequiredMixin, CommonFormView):
    template_name = 'ppt/report_search.html'
    form_class = forms.ReportSearchForm
    h1 = gettext_lazy("Project Planning Reports")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        report = int(form.cleaned_data["report"])
        year = nz(form.cleaned_data["year"], "None")
        region = nz(form.cleaned_data["region"], "None")
        division = nz(form.cleaned_data["division"], "None")
        section = nz(form.cleaned_data["section"], "None")

        if report == 1:
            return HttpResponseRedirect(reverse("ppt:culture_committee_report"))
        elif report == 2:
            return HttpResponseRedirect(reverse("ppt:export_csrf_submission_list") + f'?year={year}&region={region}')
        elif report == 3:
            return HttpResponseRedirect(reverse("ppt:export_project_status_summary") + f'?year={year}&region={region}')
        elif report == 4:
            return HttpResponseRedirect(
                reverse("ppt:export_project_list") + f'?year={year}&section={section}&region={region}')
        elif report == 5:
            return HttpResponseRedirect(reverse("ppt:export_sar_workplan") + f'?year={year}&region={region}')
        elif report == 6:
            return HttpResponseRedirect(reverse("ppt:export_rsa") + f'?year={year}&region={region}')
        elif report == 7:
            return HttpResponseRedirect(reverse("ppt:export_ppa") + f'?year={year}&section={section}&region={region}')
        elif report == 8:
            return HttpResponseRedirect(
                reverse("ppt:export_costs") + f'?year={year}&section={section}&division={division}&region={region}')
        elif report == 9:
            return HttpResponseRedirect(
                reverse("ppt:export_eqp") + f'?year={year}&section={section}&division={division}&region={region}')
        elif report == 10:
            return HttpResponseRedirect(
                reverse("ppt:export_staff") + f'?year={year}&section={section}&division={division}&region={region}')
        elif report == 11:
            return HttpResponseRedirect(
                reverse("ppt:export_lab") + f'?year={year}&section={section}&division={division}&region={region}')
        elif report == 12:
            return HttpResponseRedirect(
                reverse("ppt:export_cost_descriptions"))
        else:
            messages.error(self.request, "Report is not available. Please select another report.")
            return HttpResponseRedirect(reverse("ppt:reports"))


@login_required()
def culture_committee_report(request):
    # year = None if request.GET.get("year") == "None" else int(request.GET.get("year"))
    file_url = reports.generate_culture_committee_report()

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response[
                'Content-Disposition'] = f'inline; filename="dmapps culture committee report ({timezone.now().strftime("%Y-%m-%d")}).xlsx"'

            return response
    raise Http404


@login_required()
def export_acrdp_application(request, pk):
    project = get_object_or_404(models.Project, pk=pk)

    # check if the project lead's profile is up-to-date
    if not project.lead_staff.exists():
        messages.error(request, _("Warning: There are no lead staff on this project!!"))
    else:
        if not project.lead_staff.first().user.profile.tposition:
            messages.error(request,
                           _("Warning: project lead's profile information is missing in DM Apps (position title)"))
        if not project.lead_staff.first().user.profile.phone:
            messages.error(request,
                           _("Warning: project lead's profile information is missing in DM Apps (phone number)"))
    file_url = reports.generate_acrdp_application(project)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-word")
            response['Content-Disposition'] = f'inline; filename="ACRDP application (Project ID {project.id}).docx"'
            return response
    raise Http404


@login_required()
def export_acrdp_budget(request, pk):
    project = get_object_or_404(models.Project, pk=pk)

    # check if the project lead's profile is up-to-date
    if project.lead_staff.first() and not project.lead_staff.first().user.profile.tposition:
        messages.error(request, _("Warning: project lead's profile information is missing in DM Apps (position title)"))
    if project.lead_staff.first() and not project.lead_staff.first().user.profile.phone:
        messages.error(request, _("Warning: project lead's profile information is missing in DM Apps (phone number)"))
    file_url = reports.generate_acrdp_budget(project)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; filename="ACRDP Budget (Project ID {project.id}).xls"'
            return response
    raise Http404


@login_required()
def csrf_application(request, pk):
    project = get_object_or_404(models.Project, pk=pk)

    # check if the project lead's profile is up-to-date
    if not project.lead_staff.exists():
        messages.error(request, _("Warning: There are no lead staff on this project!!"))
    # else:
    #     if not project.lead_staff.first().user.profile.tposition:
    #         messages.error(request, _("Warning: project lead's profile information is missing in DM Apps (position title)"))
    #     if not project.lead_staff.first().user.profile.phone:
    #         messages.error(request, _("Warning: project lead's profile information is missing in DM Apps (phone number)"))
    lang = get_language()
    file_url = reports.generate_csrf_application(project, lang)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-word")
            if lang == "fr":
                filename = f'demande de FRSC (no. projet {project.id}).docx'
            else:
                filename = f'CSRF application (Project ID {project.id}).docx'

            response['Content-Disposition'] = f'inline; filename="{filename}"'
            return response
    raise Http404


@login_required()
def sara_application(request, pk):
    project = get_object_or_404(models.Project, pk=pk)

    # check if the project lead's profile is up-to-date
    if not project.lead_staff.exists():
        messages.error(request, _("Warning: There are no lead staff on this project!!"))
    lang = get_language()
    file_url = reports.generate_sara_application(project, lang)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-word")
            if lang == "fr":
                filename = f'demande de SARA (no. projet {project.id}).docx'
            else:
                filename = f'SARA application (Project ID {project.id}).docx'

            response['Content-Disposition'] = f'inline; filename="{filename}"'
            return response
    raise Http404


@login_required()
def export_csrf_submission_list(request):
    year = request.GET.get("year")
    region = request.GET.get("region")

    file_url = reports.generate_csrf_submission_list(year, region)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response[
                'Content-Disposition'] = f'inline; filename="CSRF Regional List of Submissions ({timezone.now().strftime("%Y-%m-%d")}).xls"'
            return response
    raise Http404


@login_required()
def project_status_summary(request):
    year = request.GET.get("year") if "year" in request.GET else request.GET.get("fiscal_year")
    region = request.GET.get("region")
    # Create the HttpResponse object with the appropriate CSV header.
    response = reports.generate_project_status_summary(year, region)
    response[
        'Content-Disposition'] = f'attachment; filename="project status summary ({timezone.now().strftime("%Y %m %d")}).csv"'
    return response


@login_required()
def export_project_list(request):
    qs = get_project_year_queryset(request)
    # Create the HttpResponse object with the appropriate CSV header.
    response = reports.generate_project_list(qs)
    response['Content-Disposition'] = f'attachment; filename="project list ({timezone.now().strftime("%Y %m %d")}).csv"'
    return response


@login_required()
def export_cost_descriptions(request):
    file_url = reports.generate_cost_descriptions()
    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; filename="ppt cost descriptions.xlsx"'
            return response


@login_required()
def export_py_list(request):
    qs = get_project_year_queryset(request)

    site_url = my_envr(request)["SITE_FULL_URL"]

    get_collab = False
    if request.GET.get("get_collaborations"):
        get_collab = True

    if request.GET.get("long"):
        file_url = reports.generate_py(qs, site_url, "long", get_collab)
    else:
        file_url = reports.generate_py(qs, site_url, "basic", get_collab)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; filename="project export (basic).xlsx"'
            return response
    raise Http404


@login_required()
def export_sar_workplan(request):
    year = request.GET.get("year") if "year" in request.GET else request.GET.get("fiscal_year")
    region = request.GET.get("region")
    region_name = None
    # Create the HttpResponse object with the appropriate CSV header.
    if region and region != "None":
        region_name = shared_models.Region.objects.get(pk=region)

    file_url = reports.generate_sar_workplan(year, region)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            if region_name:
                response[
                    'Content-Disposition'] = f'inline; filename="({year}) {region_name} - SAR Science workingplan.xls"'
            else:
                response['Content-Disposition'] = f'inline; filename="({year}) - SAR Science workingplan.xls"'

            return response
    raise Http404


@login_required()
def export_regional_staff_allocation(request):
    year = request.GET.get("year") if "year" in request.GET else request.GET.get("fiscal_year")
    region = request.GET.get("region")
    # Create the HttpResponse object with the appropriate CSV header.
    region_name = None
    if region:
        region_name = shared_models.Region.objects.get(pk=region)

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}_region_({}).csv"'.format(region_name, year)

    writer = csv.writer(response)
    writer.writerow(['Staff_Member', 'Fiscal_Year', 'Draft', 'Submitted_Unapproved', 'Approved'])

    project_years = models.ProjectYear.objects.filter(fiscal_year_id=year,
                                                      project__section__division__branch__region_id=region).values('pk')
    users = User.objects.filter(staff_instances2__project_year_id__in=project_years).distinct().order_by("last_name")

    for u in users:
        my_dict = get_user_fte_breakdown(u, fiscal_year_id=year)
        writer.writerow([my_dict["name"], my_dict["fiscal_year"], my_dict["draft"], my_dict["submitted_unapproved"],
                         my_dict["approved"]])

    return response


@login_required()
def export_project_position_allocation(request):
    project_years = get_project_year_queryset(request)

    year = request.GET.get("year") if "year" in request.GET else request.GET.get("fiscal_year")
    region = request.GET.get("region")
    section = request.GET.get("section")

    region_name = None
    if region:
        region_name = shared_models.Region.objects.get(pk=region)

    section_name = None
    if section:
        section_name = shared_models.Section.objects.get(pk=section)

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    if section_name:
        response['Content-Disposition'] = 'attachment; filename="{}_{}_{}.csv"'.format(year, region_name, section_name)
    else:
        response['Content-Disposition'] = 'attachment; filename="{}_{}.csv"'.format(year, region_name)

    writer = csv.writer(response)
    writer.writerow(['Project ID', 'Project Name', 'Project Lead', 'Staff Name', 'Staff Level', 'Funding Source'])

    # Now filter down the projects to projects that have staff with staff levels, but no staff name.
    for p in project_years:
        staff = p.staff_set.filter(user__id=None)
        if staff:
            leads = ", ".join(l.smart_name for l in p.staff_set.filter(is_lead=True))
            project = p.project
            for s in staff:
                # sometimes people enter a persons name
                writer.writerow([project.pk, project.title, '"' + leads + '"', s.smart_name, s.level, s.funding_source])

    return response


@login_required()
def export_costs(request):
    qs = get_project_year_queryset(request)
    site_url = my_envr(request)["SITE_FULL_URL"]
    file_url = reports.generate_cost_report(qs, site_url)
    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; filename="ppt project costs.xlsx"'
            return response
    raise Http404


@login_required()
def export_equipment_summary(request):
    year = request.GET.get("year") if "year" in request.GET else request.GET.get("fiscal_year")
    section = request.GET.get("section")

    section_name = None
    if section and section != 'None':
        section_name = shared_models.Section.objects.get(pk=section)

    project_years = models.ProjectYear.objects.filter(fiscal_year_id=year,
                                                      project__section_id=section)

    status_list = models.ProjectYear.status_choices
    status = {status_list[i][0]: status_list[i][1] for i in range(0, len(status_list))}

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}_{}_equipment_summary.csv"'.format(year, section_name)

    writer = csv.writer(response)
    writer.writerow([
        'ID',
        'Status',
        'Title',
        'Section',
        'Functional group',
        'Start date of project',
        'End date of project',
        'Project years',
        'Project leads',
        'Project overview',

        'Des. Need for Vehicle',
        'Ship',
        'COIP number',
        'Insturments',
    ])

    for p in project_years:
        years = ", ".join([y.fiscal_year.full for y in p.project.years.all()])
        leads_as_users = p.get_project_leads_as_users()
        leads = ""
        if leads_as_users:
            leads = ", ".join([u.first_name + " " + u.last_name for u in leads_as_users])

        writer.writerow([p.project.pk, status.get(p.status), p.project.title, section_name, p.project.functional_group,
                         p.start_date, p.end_date, years, leads, p.project.overview,

                         p.vehicle_needs, p.ship_needs, p.coip_reference_id, p.instrumentation])
    return response


@login_required()
def export_field_staff_summary(request):
    year = request.GET.get("year") if "year" in request.GET else request.GET.get("fiscal_year")
    section = request.GET.get("section")

    section_name = None
    if section and section != 'None':
        section_name = shared_models.Section.objects.get(pk=section)

    project_years = models.ProjectYear.objects.filter(fiscal_year_id=year,
                                                      project__section_id=section)

    status_list = models.ProjectYear.status_choices
    status = {status_list[i][0]: status_list[i][1] for i in range(0, len(status_list))}

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}_{}_field_staff_summary.csv"'.format(year, section_name)

    writer = csv.writer(response)
    writer.writerow([
        'ID',
        'Approved',
        'Title',
        'Section',
        'Functional group',
        'Start date of project',
        'End date of project',
        'Project years',
        'Project leads',
        'Project overview',

        'Requires Field Support Staff',
        'Support Details',
    ])

    for p in project_years:
        years = ", ".join([y.fiscal_year.full for y in p.project.years.all()])
        leads_as_users = p.get_project_leads_as_users()
        leads = ""
        if leads_as_users:
            leads = ", ".join([u.first_name + " " + u.last_name for u in leads_as_users])

        writer.writerow([p.project.pk, status.get(p.status), p.project.title, section_name, p.project.functional_group,
                         p.start_date, p.end_date, years, leads, p.project.overview,

                         p.requires_field_staff, p.field_staff_needs])
    return response


@login_required()
def export_lab_summary(request):
    year = request.GET.get("year") if "year" in request.GET else request.GET.get("fiscal_year")
    section = request.GET.get("section")

    section_name = None
    if section and section != 'None':
        section_name = shared_models.Section.objects.get(pk=section)

    project_years = models.ProjectYear.objects.filter(fiscal_year_id=year, project__section_id=section)

    status_list = models.ProjectYear.status_choices
    status = {status_list[i][0]: status_list[i][1] for i in range(0, len(status_list))}

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}_{}_lab_summary.csv"'.format(year, section_name)

    writer = csv.writer(response)
    writer.writerow([
        'ID',
        'Approved',
        'Title',
        'Section',
        'Functional group',
        'Start date of project',
        'End date of project',
        'Project years',
        'Project leads',
        'Project overview',

        'Requires Lab Work',
        'Is Lab Space Required',
        'Specialized Support',
        'Other Lab Requirements',
    ])

    for p in project_years:
        years = ", ".join([y.fiscal_year.full for y in p.project.years.all()])
        leads_as_users = p.get_project_leads_as_users()
        leads = ""
        if leads_as_users:
            leads = ", ".join([u.first_name + " " + u.last_name for u in leads_as_users])

        writer.writerow([p.project.pk, status.get(p.status), p.project.title, section_name, p.project.functional_group,
                         p.start_date, p.end_date, years, leads, p.project.overview,

                         p.has_lab_component, p.requires_lab_space,
                         p.requires_other_lab_support, p.other_lab_support_needs])
    return response


@login_required()
def export_project_summary(request):
    file_url = reports.export_project_summary(request)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            year = request.GET.get('fiscal_year')
            region_name = request.GET.get('region') if request.GET.get('region') != 'null' else None
            if region_name:
                response['Content-Disposition'] = f'inline; filename="({year}) {region_name} - Project Summary.xls"'
            else:
                response['Content-Disposition'] = f'inline; filename="({year}) - Project Summary.xls"'

            return response
    raise Http404




