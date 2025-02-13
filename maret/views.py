import json
import math
import os

import shared_models.models
from django.views import View

from ihub.models import Status
from ihub.utils import in_ihub_edit_group
from maret.reports import InteractionReport, CommitteeReport, OrganizationReport, PersonReport
from shared_models.views import CommonTemplateView, CommonFilterView, CommonCreateView, CommonFormsetView, \
    CommonDetailView, CommonDeleteView, CommonUpdateView, CommonPopoutUpdateView, CommonPopoutCreateView, \
    CommonPopoutDeleteView, CommonHardDeleteView

from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404

from django.utils import timezone
from django.utils.translation import gettext as _, gettext_lazy
from django.utils.safestring import mark_safe

from django.db.models import TextField, Value
from django.db.models.functions import Concat

from django.urls import reverse_lazy, reverse

from maret.utils import MaretBasicRequiredMixin, UserRequiredMixin, AuthorRequiredMixin, AdminRequiredMixin, \
    AdminOrSuperuserRequiredMixin
from maret import models, filters, forms, utils, reports

from masterlist import models as ml_models

from easy_pdf.views import PDFTemplateView


class MaretUserFormsetView(AdminOrSuperuserRequiredMixin, CommonFormsetView):
    template_name = 'maret/formset.html'
    h1 = "Manage Maret Administrative Users"
    queryset = models.MaretUser.objects.all()
    formset_class = forms.MaretUserFormset
    success_url_name = "maret:manage_maret_users"
    home_url_name = "maret:index"
    delete_url_name = "maret:delete_maret_user"


class MaretUserHardDeleteView(AdminOrSuperuserRequiredMixin, CommonHardDeleteView):
    model = models.MaretUser
    success_url = reverse_lazy("maret:manage_maret_users")


#######################################################
# Application Help text controls
#######################################################
class CommonCreateViewHelp(CommonCreateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['help_text_dict'] = utils.get_help_text_dict(self.model)

        # if the UserMode table has this user in "edit" mode provide the
        # link to the dialog to manage help text via the manage_help_url
        # and provide the model name the help text will be assigned to.
        # The generic_form_with_help_text.html from the shared_models app
        # will provide the field name and together you have the required
        # model and field needed to make an entry in the Help Text table.
        if self.request.user.maret_user.mode == 2:
            context['manage_help_url'] = "maret:manage_help_text"
            context['model_name'] = self.model.__name__

        return context


class CommonUpdateViewHelp(CommonUpdateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['help_text_dict'] = utils.get_help_text_dict(self.model)

        # if the UserMode table has this user in "edit" mode provide the
        # link to the dialog to manage help text via the manage_help_url
        # and provide the model name the help text will be assigned to.
        # The generic_form_with_help_text.html from the shared_models app
        # will provide the field name and together you have the required
        # model and field needed to make an entry in the Help Text table.
        if self.request.user.maret_user.mode == 2:
            context['manage_help_url'] = "maret:manage_help_text"
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


# Controls the administrative helptext page that allows all entries to be viewed, modified and deleted
class HelpTextFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'maret/formset.html'
    title = _("MarET Help Text")
    h1 = _("Manage Help Texts")
    queryset = models.HelpText.objects.all()
    formset_class = forms.HelpTextFormset
    success_url_name = "maret:manage_help_texts"
    home_url_name = "maret:index"
    delete_url_name = "maret:delete_help_text"


class HelpTextHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = models.HelpText
    success_url = reverse_lazy("maret:manage_help_texts")


#######################################################
# Home page view
#######################################################
class IndexView(MaretBasicRequiredMixin, CommonTemplateView):
    h1 = "home"
    template_name = 'maret/index.html'

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, mark_safe(
            _("Please note that only <b>unclassified information</b> may be entered into this application.")))
        return super().dispatch(request, *args, **kwargs)


#######################################################
# Person
#######################################################
class PersonListView(UserRequiredMixin, CommonFilterView):
    template_name = 'maret/maret_list.html'
    filterset_class = filters.PersonFilter
    model = ml_models.Person
    queryset = ml_models.Person.objects.annotate(
        search_term=Concat(
            'first_name', Value(' '),
            'last_name', Value(' '),
            'designation', Value(' '),
            'notes', Value(' '),
            output_field=TextField()))
    field_list = [
        {"name": 'full_name_with_title|{}'.format(_("full name")), "class": "", "width": ""},
        {"name": 'organizations', "class": "", "width": ""},
        {"name": 'date_last_modified|{}'.format(_("last updated")), "class": "", "width": ""},
    ]
    new_object_url_name = "maret:person_new"
    row_object_url_name = "maret:person_detail"
    home_url_name = "maret:index"
    paginate_by = 100
    h1 = _("Contacts")
    container_class = "container-fluid"

    def get_context_data(self, **kwargs):
        # we want to update the context with the context vars added by CommonMixin classes
        context = super().get_context_data(**kwargs)
        filtered_ids = [person.pk for person in self.filterset.qs]
        context["report_url"] = reverse_lazy("maret:person_report") + "?ids=" + str(filtered_ids)
        return context


class PersonDetailView(UserRequiredMixin, CommonDetailView):
    model = ml_models.Person
    template_name = 'maret/person_detail.html'
    field_list = [
        "designation",
        "first_name",
        "last_name",
        "phone_1",
        "phone_2",
        "email_1",
        "email_2",
        "cell",
        "fax",
        "language",
        "notes",
        "email_block",
        "date_last_modified",
        "last_modified_by",
    ]
    home_url_name = "maret:index"
    parent_crumb = {"title": gettext_lazy("Contacts"), "url": reverse_lazy("maret:person_list")}


class PersonCreateView(AuthorRequiredMixin, CommonCreateViewHelp):
    model = ml_models.Person
    form_class = forms.PersonForm
    parent_crumb = {"title": gettext_lazy("Person"), "url": reverse_lazy("maret:person_list")}
    template_name = "maret/form.html"
    h1 = gettext_lazy("New Contact")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.last_modified_by = self.request.user
        obj.created_by = self.request.user
        super().form_valid(form)

        ext_con = None
        fields = form.cleaned_data

        return HttpResponseRedirect(reverse_lazy('maret:person_detail', kwargs={'pk': obj.id}))


class PersonUpdateView(AuthorRequiredMixin, CommonUpdateViewHelp):
    model = ml_models.Person
    form_class = forms.PersonForm
    parent_crumb = {"title": gettext_lazy("Person"), "url": reverse_lazy("maret:person_list")}
    template_name = "maret/form.html"
    h1 = gettext_lazy("Contact")

    def get_initial(self):
        committees = []
        if models.Committee.objects.filter(external_contact__in=[self.object]):
            committees_qs = models.Committee.objects.filter(external_contact__in=[self.object])
            committees = [c.pk for c in committees_qs]

        return {
            'committee': committees,
        }

    def form_valid(self, form):
        obj = form.save(commit=False)
        if obj.locked_by_ihub:
            messages.error(self.request, _("This record can only be modified through iHub"))
            return HttpResponseRedirect(reverse("maret:person_detail", args=[obj.pk, ]))
        obj.last_modified_by = self.request.user
        obj.save()

        ext_con = None
        if models.ContactExtension.objects.filter(contact=obj):
            ext_con = models.ContactExtension.objects.get(contact=obj)

        fields = form.cleaned_data
        if fields['committee']:
            for com_id in fields['committee']:
                com = models.Committee.objects.get(id=com_id)
                com.external_contact.add(obj)
                com.save()

        return super().form_valid(form)


class PersonCreateViewPopout(AuthorRequiredMixin, CommonPopoutCreateView):
    model = ml_models.Person
    form_class = forms.PersonForm
    h1 = gettext_lazy("New Contact")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.last_modified_by = self.request.user
        obj.created_by = self.request.user
        obj.save()
        return super().form_valid(form)



class PersonUpdateViewPopout(AuthorRequiredMixin, CommonPopoutUpdateView):
    model = ml_models.Person
    form_class = forms.PersonForm
    parent_crumb = {"title": gettext_lazy("Person"), "url": reverse_lazy("maret:person_list")}
    template_name = 'shared_models/generic_popout_form.html'
    h1 = gettext_lazy("Contact")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.last_modified_by = self.request.user
        obj.save()
        return super().form_valid(form)


class PersonDeleteView(AdminRequiredMixin, CommonDeleteView):
    model = ml_models.Person
    template_name = 'maret/confirm_delete.html'
    success_url = reverse_lazy('maret:person_list')
    home_url_name = "maret:index"
    grandparent_crumb = {"title": gettext_lazy("Contacts"), "url": reverse_lazy("maret:person_list")}
    non_blocking_fields = ["ext_con"]

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("maret:person_detail", args=[self.get_object().id])}

    def delete(self, request, *args, **kwargs):
        obj = ml_models.Person.objects.get(pk=kwargs['pk'])
        if obj.locked_by_ihub:
            messages.error(self.request, _("This record can only be modified through iHub"))
            return HttpResponseRedirect(reverse("maret:person_detail", args=[obj.pk, ]))

        return super().delete(request, *args, **kwargs)


class PersonReportView(UserRequiredMixin, View):
    def get(self, request):
        id_list = json.loads(request.GET.get("ids"))
        qs = ml_models.Person.objects.filter(pk__in=id_list)

        file_url = None
        if qs:
            file_url = reports.generate_maret_report(qs, PersonReport)

        if os.path.exists(file_url):
            with open(file_url, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = f'inline; filename="MarET_person_report.xlsx"'

                return response
        raise Http404


#######################################################
# Interactions
#######################################################
class InteractionListView(UserRequiredMixin, CommonFilterView):
    template_name = 'maret/interaction_list.html'
    queryset = models.Interaction.objects.all().distinct().annotate(
        search_term=Concat(
            'description', Value(' '),
            'comments', Value(' '),
            'action_items', Value(' '),
            output_field=TextField()))
    filterset_class = filters.InteractionFilter
    model = models.Interaction
    field_list = [
        {"name": 'description', "class": "", "width": ""},
        {"name": 'interaction_type', "class": "", "width": ""},
        {"name": 'date_of_meeting|Date of interaction (YYYY-MM-DD)', "class": "", "width": ""},
        {"name": 'main_topic', "class": "", "width": ""},
        {"name": 'species', "class": "", "width": ""},
    ]
    new_object_url_name = "maret:interaction_new"
    row_object_url_name = "maret:interaction_detail"
    home_url_name = "maret:index"

    def get_context_data(self, **kwargs):
        # we want to update the context with the context vars added by CommonMixin classes
        context = super().get_context_data(**kwargs)
        filtered_ids = [interaction.pk for interaction in context["object_list"]]
        context["report_url"] = reverse_lazy("maret:interaction_report") + "?ids=" + str(filtered_ids)
        return context


class InteractionCreateView(AuthorRequiredMixin, CommonCreateViewHelp):
    model = models.Interaction
    form_class = forms.InteractionForm
    parent_crumb = {"title": gettext_lazy("Interaction"), "url": reverse_lazy("maret:interaction_list")}
    template_name = "maret/form.html"
    h1 = gettext_lazy("New Interaction")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['scripts'] = ['maret/js/divisionFilter.html', 'maret/js/areaOfficeProgramFilter.html',
                              'maret/js/interactionForm.html']

        return context

    def form_valid(self, form):
        super(InteractionCreateView, self).form_valid(form)
        self.object = form.save(commit=False)
        self.object.last_modified_by = self.request.user
        self.object.created_by = self.request.user
        self.object.save()
        if self.object.is_committee or self.object.interaction_type == 4:
            committee = self.object.committee
            self.object.main_topic.set(committee.main_topic.all())
            self.object.external_contact.set(committee.external_contact.all())
            self.object.external_organization.set(committee.external_organization.all())
            self.object.species.set(committee.species.all())
            self.object.lead_region = committee.lead_region
            self.object.lead_national_sector = committee.lead_national_sector
            self.object.branch = committee.branch
            self.object.division = committee.division
            self.object.area_office = committee.area_office
            self.object.area_office_program = committee.area_office_program
            self.object.save()
        return HttpResponseRedirect(reverse_lazy('maret:interaction_detail', kwargs={'pk': self.object.id}))


class InteractionUpdateView(AuthorRequiredMixin, CommonUpdateViewHelp):
    model = models.Interaction
    form_class = forms.InteractionForm
    home_url_name = "maret:index"
    grandparent_crumb = {"title": gettext_lazy("Interaction"),
                         "url": reverse_lazy("maret:interaction_list")}
    template_name = "maret/form.html"

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("maret:interaction_detail", args=[self.get_object().id])}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['scripts'] = ['maret/js/divisionFilter.html', 'maret/js/areaOfficeProgramFilter.html',
                              'maret/js/interactionForm.html']
        return context

    def form_valid(self, form):
        super(InteractionUpdateView, self).form_valid(form)
        initial_committee = self.get_object().committee
        obj = form.save(commit=False)
        obj.last_modified_by = self.request.user
        obj.save()

        if obj.is_committee or obj.interaction_type == 4:
            if obj.committee != initial_committee:
                committee = obj.committee
                obj.main_topic.set(committee.main_topic.all())
                obj.species.set(committee.species.all())
                obj.external_contact.set(committee.external_contact.all())
                obj.external_organization.set(committee.external_organization.all())
                obj.lead_region = committee.lead_region
                obj.lead_national_sector = committee.lead_national_sector
                obj.branch = committee.branch
                obj.division = committee.division
                obj.area_office = committee.area_office
                obj.area_office_program = committee.area_office_program
                obj.save()

        if not obj.is_committee and obj.committee is not None:
            obj.committee = None
            obj.save()
        return HttpResponseRedirect(reverse_lazy('maret:interaction_detail', kwargs={'pk': obj.id}))


class InteractionDetailView(UserRequiredMixin, CommonDetailView):
    model = models.Interaction
    home_url_name = "maret:index"
    parent_crumb = {"title": gettext_lazy("Interactions"), "url": reverse_lazy("maret:interaction_list")}
    container_class = "container-fluid"

    def get_h1(self):
        return self.object.description

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'interaction_type',
            'is_committee',
            'committee',
            'dfo_role',
            'dfo_liaison',
            'other_dfo_participants',
            'date_of_meeting',
            'main_topic',
            'species',
            'lead_region',
            'lead_national_sector',
            'branch',
            'division',
            'area_office',
            'area_office_program',
            'other_dfo_branch',
            'other_dfo_regions',
            'dfo_national_sectors',
            'other_dfo_areas',
            'action_items',
            'comments',
            'external_organization',
            'last_modified',
            'last_modified_by',
        ]
        return context


class InteractionDeleteView(AuthorRequiredMixin, CommonDeleteView):
    model = models.Interaction
    success_url = reverse_lazy('maret:interaction_list')
    home_url_name = "maret:index"
    grandparent_crumb = {"title": gettext_lazy("Committee"), "url": reverse_lazy("maret:interaction_list")}
    template_name = "maret/confirm_delete.html"
    delete_protection = False

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("maret:interaction_detail", args=[self.get_object().id])}


class InteractionReportView(UserRequiredMixin, View):
    def get(self, request):
        id_list = json.loads(request.GET.get("ids"))
        qs = models.Interaction.objects.filter(pk__in=id_list)

        file_url = None
        if qs:
            file_url = reports.generate_maret_report(qs, InteractionReport)

        if os.path.exists(file_url):
            with open(file_url, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = f'inline; filename="MarET_interaction_report.xlsx"'

                return response
        raise Http404


#######################################################
# Committee / Working Groups
#######################################################
class CommitteeListView(UserRequiredMixin, CommonFilterView):
    h1 = gettext_lazy("Committees / Working Groups")
    template_name = 'maret/maret_list.html'
    queryset = models.Committee.objects.all().distinct().annotate(
        search_term=Concat(
            'name', Value(" "),
            'main_actions', Value(" "),
            'comments', Value(" "),
            output_field=TextField()
        ))
    filterset_class = filters.CommitteeFilter
    model = models.Committee
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'branch', "class": "", "width": ""},
        {"name": 'area_office', "class": "", "width": ""},
        {"name": 'main_topic', "class": "", "width": ""},
        {"name": 'species', "class": "", "width": ""},
    ]
    new_object_url_name = "maret:committee_new"
    row_object_url_name = "maret:committee_detail"
    home_url_name = "maret:index"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['scripts'] = ['maret/js/divisionFilter.html']
        filtered_ids = [committee.pk for committee in context["object_list"]]
        context["report_url"] = reverse_lazy("maret:committee_report") + "?ids=" + str(filtered_ids)
        return context


class CommitteeCreateView(UserRequiredMixin, CommonCreateViewHelp):
    model = models.Committee
    form_class = forms.CommitteeForm
    parent_crumb = {"title": gettext_lazy("Committees / Working Groups"), "url": reverse_lazy("maret:committee_list")}
    template_name = "maret/form.html"
    h1 = gettext_lazy("Committees / Working Groups")

    def get_initial(self):
        return {
            'branch': 0,
        }

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.last_modified_by = self.request.user
        obj.created_by = self.request.user
        obj.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['scripts'] = ['maret/js/divisionFilter.html', 'maret/js/areaOfficeProgramFilter.html',
                              'maret/js/committeeForm.html']
        return context


class CommitteeDetailView(UserRequiredMixin, CommonDetailView):
    model = models.Committee
    home_url_name = "maret:index"
    parent_crumb = {"title": gettext_lazy("Committees / Working Groups"), "url": reverse_lazy("maret:committee_list")}
    container_class = "container-fluid"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'name',
            'main_topic',
            'species',
            'lead_region',
            'lead_national_sector',
            'branch',
            'division',
            'area_office',
            'area_office_program',
            'is_dfo_chair',
            'external_chair',
            'dfo_liaison',
            'other_dfo_branch',
            'other_dfo_regions',
            'dfo_national_sectors',
            'other_dfo_areas',
            'dfo_role',
            'first_nation_participation',
            'municipal_participation',
            'provincial_participation',
            'other_federal_participation',
            'other_dfo_participants',
            'meeting_frequency',
            'are_tor',
            'location_of_tor',
            'area_office',
            'main_actions',
            'comments',
            "last_modified",
            "last_modified_by",
        ]

        return context


class CommitteeDeleteView(AuthorRequiredMixin, CommonDeleteView):
    model = models.Committee
    success_url = reverse_lazy('maret:committee_list')
    home_url_name = "maret:index"
    grandparent_crumb = {"title": gettext_lazy("Committees / Working Groups"),
                         "url": reverse_lazy("maret:committee_list")}
    template_name = "maret/confirm_delete.html"
    delete_protection = True

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("maret:committee_detail", args=[self.get_object().id])}


class CommitteeUpdateView(AuthorRequiredMixin, CommonUpdateViewHelp):
    model = models.Committee
    form_class = forms.CommitteeForm
    home_url_name = "maret:index"
    grandparent_crumb = {"title": gettext_lazy("Committees / Working Groups"),
                         "url": reverse_lazy("maret:committee_list")}
    h1 = gettext_lazy("Committees / Working Groups")
    template_name = "maret/form.html"

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("maret:committee_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.last_modified_by = self.request.user
        obj.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['scripts'] = ['maret/js/divisionFilter.html', 'maret/js/areaOfficeProgramFilter.html',
                              'maret/js/committeeForm.html']
        return context


class CommitteeReportView(UserRequiredMixin, View):
    def get(self, request):
        id_list = json.loads(request.GET.get("ids"))
        qs = models.Committee.objects.filter(pk__in=id_list)

        file_url = None
        if qs:
            file_url = reports.generate_maret_report(qs, CommitteeReport)

        if os.path.exists(file_url):
            with open(file_url, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = f'inline; filename="MarET_committee_report.xlsx"'

                return response
        raise Http404


#######################################################
# Organization
#######################################################
class OrganizationListView(UserRequiredMixin, CommonFilterView):
    template_name = 'maret/organization_list.html'
    queryset = ml_models.Organization.objects.all().distinct().annotate(
        search_term=Concat(
            'name_eng', Value(" "),
            'abbrev', Value(" "),
            'name_ind', Value(" "),
            'notes', Value(" "),
            output_field=TextField()))
    filterset_class = filters.OrganizationFilter
    paginate_by = 25
    field_list = [
        {"name": 'name_eng', "class": "", "width": ""},
        {"name": 'category', "class": "", "width": ""},
        {"name": 'grouping', "class": "", "width": ""},
        {"name": 'area', "class": "", "width": ""},
        {"name": 'province', "class": "", "width": ""},
        {"name": 'regions', "class": "", "width": ""},
    ]
    home_url_name = "maret:index"
    new_object_url_name = "maret:org_new"
    row_object_url_name = "maret:org_detail"
    container_class = "container-fluid"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filtered_ids = [org.pk for org in self.filterset.qs]
        context["report_url"] = reverse_lazy("maret:org_report") + "?ids=" + str(filtered_ids)
        return context


class OrganizationCreateView(AuthorRequiredMixin, CommonCreateViewHelp):
    model = ml_models.Organization
    template_name = 'maret/form.html'
    form_class = forms.OrganizationForm
    home_url_name = "maret:index"
    parent_crumb = {"title": gettext_lazy("Organizations"), "url": reverse_lazy("maret:org_list")}
    is_multipart_form_data = True
    h1 = gettext_lazy("New Organization")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.last_modified_by = self.request.user
        obj.save()
        super().form_valid(form)

        ext_org = None
        fields = form.cleaned_data
        if fields['area']:
            if not ext_org:
                ext_org = models.OrganizationExtension(organization=obj)
                ext_org.save()
            ext_org.area.set(fields['area'])
            ext_org.save()

        if fields['asc_province']:
            if not ext_org:
                ext_org = models.OrganizationExtension(organization=obj)
                ext_org.save()
            ext_org.associated_provinces.set(fields['asc_province'])
            ext_org.save()

        if fields['committee']:
            for committee_pk in fields["committee"]:
                committee = models.Committee.objects.get(pk=committee_pk)
                committee.external_organization.add(obj.pk)
                committee.save()

        return HttpResponseRedirect(reverse_lazy('maret:org_detail', kwargs={'pk': obj.id}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['scripts'] = ['maret/js/organizationForm.html']

        return context


class OrganizationDetailView(UserRequiredMixin, CommonDetailView):
    model = ml_models.Organization
    template_name = 'maret/organization_detail.html'
    field_list = [
        'name_eng',
        'former_name',
        'abbrev',
        'email',
        'address',
        'mailing_address',
        'city',
        'postal_code',
        'province',
        'phone',
        'fax',
        'grouping',
        'regions',
        'website',
        'category',
        'date_last_modified',
        'last_modified_by'
    ]
    home_url_name = "maret:index"
    parent_crumb = {"title": gettext_lazy("Organizations"), "url": reverse_lazy("maret:org_list")}
    container_class = "container-fluid"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org = self.get_object()

        entries_dict = dict()
        if self.request.user.is_authenticated:
            if org.entries.exists():
                entries = org.entries.all()
                statuses = Status.objects.filter(entries__in=entries).distinct()
                for status in statuses:
                    entries_dict[status] = entries.filter(status=status).order_by("initial_date", "title")

        context["entries"] = entries_dict
        return context


class OrganizationUpdateView(AuthorRequiredMixin, CommonUpdateViewHelp):
    model = ml_models.Organization
    template_name = 'maret/form.html'
    form_class = forms.OrganizationForm
    home_url_name = "maret:index"
    parent_crumb = {"title": gettext_lazy("Organizations"), "url": reverse_lazy("maret:org_list")}
    is_multipart_form_data = True

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("maret:org_detail", args=[self.get_object().id])}

    def get_initial(self):
        areas = []
        asc_province = []
        committees = []
        if models.OrganizationExtension.objects.filter(organization=self.object):
            ext_org = models.OrganizationExtension.objects.get(organization=self.object)
            if ext_org:
                areas = [a.pk for a in ext_org.area.all()]
                asc_province = [p.pk for p in ext_org.associated_provinces.all()]
        if models.Committee.objects.filter(external_organization__in=[self.object]):
            committees_qs = models.Committee.objects.filter(external_organization__in=[self.object])
            committees = [c.pk for c in committees_qs]

        return {
            'area': areas,
            'committee': committees,
            'asc_province': asc_province,
        }

    def form_valid(self, form):
        obj = form.save(commit=False)
        if obj.locked_by_ihub:
            messages.error(self.request, _("This record can only be modified through iHub"))
            return HttpResponseRedirect(reverse("maret:org_detail", args=[obj.pk, ]))

        obj.last_modified_by = self.request.user
        obj.save()

        ext_org = None
        if models.OrganizationExtension.objects.filter(organization=obj):
            ext_org = models.OrganizationExtension.objects.get(organization=obj)

        fields = form.cleaned_data
        if fields['area']:
            if not ext_org:
                ext_org = models.OrganizationExtension(organization=obj)
                ext_org.save()
            ext_org.area.set(fields['area'])
            ext_org.save()


        if fields['asc_province']:
            if not ext_org:
                ext_org = models.OrganizationExtension(organization=obj)
                ext_org.save()
            ext_org.associated_provinces.set(fields['asc_province'])
            ext_org.save()

        if fields['email']:
            if not ext_org:
                ext_org = models.OrganizationExtension(organization=obj)
                ext_org.save()
            # set field directly to avoid calling set on none type
            ext_org.email = fields["email"]
            ext_org.save()

        if fields['committee']:
            for committee_pk in fields["committee"]:
                committee = models.Committee.objects.get(pk=committee_pk)
                committee.external_organization.add(obj)
                committee.save()

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['scripts'] = ['maret/js/organizationForm.html']

        return context


class OrganizationDeleteView(AdminRequiredMixin, CommonDeleteView):
    model = ml_models.Organization
    template_name = 'maret/confirm_delete.html'
    success_url = reverse_lazy('maret:org_list')
    home_url_name = "maret:index"
    grandparent_crumb = {"title": gettext_lazy("Organizations"), "url": reverse_lazy("maret:org_list")}
    non_blocking_fields = ["ext_org"]

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("maret:org_detail", args=[self.get_object().id])}

    def delete(self, request, *args, **kwargs):
        obj = ml_models.Organization.objects.get(pk=kwargs['pk'])
        if obj.locked_by_ihub:
            messages.error(self.request, _("This record can only be modified through iHub"))
            return HttpResponseRedirect(reverse("maret:org_detail", args=[obj.pk, ]))

        return super().delete(request, *args, **kwargs)

    def get_related_names(self):
        related_names_list = super(OrganizationDeleteView, self).get_related_names()
        # remove org extensions dict from this list as these will otherwise block being allowed to delete the org.
        related_names_list[:] = [d for d in related_names_list if d.get('title') != "organization extensions"]
        return related_names_list


class OrganizationCueCard(PDFTemplateView):
    template_name = "maret/report_cue_card.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org = ml_models.Organization.objects.get(pk=self.kwargs["org"])
        context["org"] = org

        context["org_field_list_1"] = [
            'name_eng',
            'former_name',
            'abbrev',
        ]
        context["org_field_list_2"] = [
            'website',
            'address',
            'mailing_address',
        ]
        context["org_field_list_3"] = [
            'city',
            'postal_code',
            'province',
        ]
        context["org_field_list_4"] = [
            'phone',
            'fax',
            'notes',
        ]

        # determine how many rows, cols for the table
        num_cols = 4
        context["contact_table_cols"] = range(0, num_cols)
        context["contact_table_rows"] = range(0, math.ceil(org.members.count() / num_cols))

        context["committee_field_list_1"] = [
            'main_topic',
            'species',
            'lead_region',
            'lead_national_sector',
            'branch',
            ]
        context["committee_field_list_2"] = [
            'area_office'
            'other_dfo_branch',
            'other_dfo_areas',
            'other_dfo_regions',
            'dfo_national_sectors',
            
        ]
        context["committee_field_list_3"] = [
            'dfo_role',
            'is_dfo_chair',
            'external_chair',
            'dfo_liaison',
            'other_dfo_participants',
        ]
        context["committee_field_list_4"] = [
            'first_nation_participation',
            'municipal_participation',
            'main_actions',
            'comments'
        ]
        context["interaction_field_list_1"] = [
            'interaction_type',
            'is_committee',
            'committee',
            'date_of_meeting',
            'main_topic',
        ]
        context["interaction_field_list_2"] = [
            'species'
            'lead_region',
            'lead_national_sector',
            'branch',
            'area_office',
        ]
        context["interaction_field_list_3"] = [
            'other_dfo_branch',
            'other_dfo_areas',
            'other_dfo_regions',
            'dfo_national_sectors',
            'dfo_role',
        ]
        context["interaction_field_list_4"] = [
            'dfo_liaison',
            'action_items',
            'comments',
        ]
        context["now"] = timezone.now()
        return context


class OrganizationReportView(UserRequiredMixin, View):

    def get(self, request):
        id_list = json.loads(request.GET.get("ids"))
        qs = ml_models.Organization.objects.filter(pk__in=id_list)

        file_url = None
        if qs:
            file_url = reports.generate_maret_report(qs, OrganizationReport)

        if os.path.exists(file_url):
            with open(file_url, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = f'inline; filename="MarET_organization_report.xlsx"'

                return response
        raise Http404


#######################################################
# Organization Memberships
#######################################################
class MemberCreateView(AuthorRequiredMixin, CommonPopoutCreateView):
    model = ml_models.OrganizationMember
    template_name = 'maret/member_form_popout.html'
    form_class = forms.MemberForm
    width = 1000
    height = 700
    h1 = gettext_lazy("New Organization Member")

    def get_initial(self):
        org = ml_models.Organization.objects.get(pk=self.kwargs['org'])
        return {
            'organization': org,
        }

    def form_valid(self, form):
        obj = form.save(commit=False)
        if obj.organization.locked_by_ihub:
            messages.error(self.request, _("This record can only be modified through iHub"))
            return HttpResponseRedirect(reverse("maret:org_detail", args=[obj.organization.pk, ]))

        obj.last_modified_by = self.request.user
        obj.save()
        return HttpResponseRedirect(self.get_success_url())


class MemberUpdateView(AuthorRequiredMixin, CommonPopoutUpdateView):
    model = ml_models.OrganizationMember
    template_name = 'maret/member_form_popout.html'
    form_class = forms.MemberForm
    width = 1000
    height = 800

    def form_valid(self, form):
        obj = form.save(commit=False)
        if obj.organization.locked_by_ihub:
            messages.error(self.request, _("This record can only be modified through iHub"))
            return HttpResponseRedirect(reverse("maret:org_detail", args=[obj.organization.pk, ]))

        obj.last_modified_by = self.request.user
        obj.save()
        return HttpResponseRedirect(self.get_success_url())


class MemberDeleteView(AdminRequiredMixin, CommonPopoutDeleteView):
    model = ml_models.OrganizationMember

    def delete(self, request, *args, **kwargs):
        obj = ml_models.OrganizationMember.objects.get(pk=kwargs['pk'])
        if obj.organization.locked_by_ihub:
            messages.error(self.request, _("This record can only be modified through iHub"))
            return HttpResponseRedirect(reverse("maret:person_detail", args=[obj.pk, ]))

        return super().delete(request, *args, **kwargs)


class UserDetailView(UserRequiredMixin, CommonDetailView):
    model = shared_models.models.User
    template_name = 'maret/user_detail.html'
    field_list = [
        "first_name",
        "last_name",
        "email",
        "section",
    ]
    home_url_name = "maret:index"
    parent_crumb = {}


class CommonMaretFormset(AdminRequiredMixin, CommonFormsetView):
    template_name = 'maret/formset.html'
    home_url_name = "maret:index"


class TopicFormsetView(CommonMaretFormset):
    h1 = _("Manage Discussion Topics")
    queryset = models.DiscussionTopic.objects.all()
    formset_class = forms.TopicFormSet
    success_url_name = "maret:manage_topics"
    # delete_url_name = "maret:delete_topics"


class SpeciesFormsetView(CommonMaretFormset):
    h1 = _("Manage Species")
    queryset = models.Species.objects.all()
    formset_class = forms.SpeciesFormSet
    success_url_name = "maret:manage_species"


class AreaFormsetView(CommonMaretFormset):
    h1 = _("Manage Areas")
    queryset = models.Area.objects.all()
    formset_class = forms.AreasFormSet
    success_url_name = "maret:manage_areas"


class AreaOfficesFormsetView(CommonMaretFormset):
    h1 = _("Manage Area Offices")
    queryset = models.AreaOffice.objects.all()
    formset_class = forms.AreaOfficesFormSet
    success_url_name = "maret:manage_area_offices"
    delete_url_name = "maret:delete_area_office"


class AreaOfficesDeleteView(AdminRequiredMixin, CommonDeleteView):
    model = models.AreaOffice
    template_name = 'maret/confirm_delete.html'
    success_url = reverse_lazy("maret:manage_area_offices")
    home_url_name = "maret:index"
    grandparent_crumb = {"title": gettext_lazy("Area Offices"), "url": reverse_lazy("maret:manage_area_offices")}
    non_blocking_fields = []

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("maret:manage_area_offices")}


class AreaOfficeProgramsFormsetView(CommonMaretFormset):
    h1 = _("Manage Area Office Programs")
    queryset = models.AreaOfficeProgram.objects.all()
    formset_class = forms.AreaOfficesProgramFormSet
    success_url_name = "maret:manage_area_office_programs"
    delete_url_name = "maret:delete_area_office_program"


class AreaOfficeProgramsDeleteView(AdminRequiredMixin, CommonDeleteView):
    model = models.AreaOfficeProgram
    template_name = 'maret/confirm_delete.html'
    success_url = reverse_lazy("maret:manage_area_office_programs")
    home_url_name = "maret:index"
    grandparent_crumb = {"title": gettext_lazy("Area Office Programs"), "url": reverse_lazy("maret:manage_area_office_programs")}
    non_blocking_fields = []

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("maret:manage_area_office_programs")}


class GroupingFormsetView(AdminRequiredMixin, CommonFormsetView):
    template_name = 'maret/formset.html'
    h1 = "Manage Groupings"
    queryset = ml_models.Grouping.objects.all()
    formset_class = forms.GroupingFormSet
    success_url_name = "maret:manage_groupings"
    home_url_name = "maret:index"


class GroupingHardDeleteView(AdminRequiredMixin, CommonHardDeleteView):
    model = ml_models.Grouping
    success_url = reverse_lazy("maret:manage_groupings")
