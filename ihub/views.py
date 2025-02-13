import math
import os
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.db.models import TextField, Value
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _, gettext_lazy
from django.views.generic import FormView, TemplateView
###
from easy_pdf.views import PDFTemplateView

from dm_apps.utils import custom_send_mail
from lib.functions.custom_functions import nz, listrify
from masterlist import models as ml_models
from shared_models.views import CommonFilterView, CommonDetailView, CommonUpdateView, CommonPopoutUpdateView, CommonPopoutCreateView, \
    CommonDeleteView, CommonCreateView, CommonHardDeleteView, CommonFormsetView, CommonPopoutDeleteView, CommonTemplateView
from . import emails
from . import filters
from . import forms
from . import models
from . import reports
from .mixins import iHubBasicMixin, iHubEditRequiredMixin, iHubAdminRequiredMixin, SuperuserOrAdminRequiredMixin
from .utils import get_date_range_overlap, in_ihub_edit_group, in_ihub_admin_group


def get_ind_organizations():
    return ml_models.Organization.objects.filter(grouping__is_indigenous=True).distinct()


class IndexTemplateView(iHubBasicMixin, CommonTemplateView):
    template_name = 'ihub/index.html'
    h1 = gettext_lazy("home")

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, mark_safe(_("Please note that only <b>unclassified information</b> may be entered into this application.")))
        return super().dispatch(request, *args, **kwargs)


# PERSON #
##########

class PersonListView(iHubBasicMixin, CommonFilterView):
    template_name = 'ihub/person_list.html'
    filterset_class = filters.PersonFilter
    model = ml_models.Person
    queryset = ml_models.Person.objects.annotate(
        search_term=Concat('first_name', 'last_name', 'designation', output_field=TextField()))
    field_list = [
        {"name": 'full_name_with_title|{}'.format(gettext_lazy("full name")), "class": "", "width": ""},
        {"name": 'phone_1', "class": "", "width": ""},
        # {"name": 'phone_2', "class": "", "width": ""},
        {"name": 'email_1', "class": "", "width": ""},
        {"name": 'last_updated|{}'.format(gettext_lazy("last updated")), "class": "", "width": ""},
    ]
    new_object_url_name = "ihub:person_new"
    row_object_url_name = "ihub:person_detail"
    home_url_name = "ihub:index"
    paginate_by = 100
    h1 = gettext_lazy("Contacts")
    container_class = "container-fluid"


class PersonDetailView(iHubBasicMixin, CommonDetailView):
    model = ml_models.Person
    template_name = 'ihub/person_detail.html'
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
        "metadata|{}".format(gettext_lazy("metadata")),
    ]
    home_url_name = "ihub:index"
    parent_crumb = {"title": gettext_lazy("Contacts"), "url": reverse_lazy("ihub:person_list")}


class PersonUpdateView(iHubEditRequiredMixin, CommonUpdateView):
    model = ml_models.Person
    template_name = 'ihub/form.html'
    form_class = forms.PersonForm
    home_url_name = "ihub:index"
    grandparent_crumb = {"title": gettext_lazy("Contacts"), "url": reverse_lazy("ihub:person_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("ihub:person_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        object = form.save(commit=False)
        object.last_modified_by = self.request.user
        object.locked_by_ihub = True
        object.save()
        return super().form_valid(form)


class PersonUpdateViewPopout(iHubEditRequiredMixin, CommonPopoutUpdateView):
    model = ml_models.Person
    form_class = forms.PersonForm

    def form_valid(self, form):
        object = form.save(commit=False)
        object.last_modified_by = self.request.user
        object.locked_by_ihub = True
        object.save()
        return super().form_valid(form)


class PersonCreateView(iHubEditRequiredMixin, CommonCreateView):
    model = ml_models.Person
    template_name = 'ihub/form.html'
    form_class = forms.PersonForm
    home_url_name = "ihub:index"
    parent_crumb = {"title": gettext_lazy("Contacts"), "url": reverse_lazy("ihub:person_list")}
    h1 = gettext_lazy("New Contact")

    def form_valid(self, form):
        object = form.save(commit=False)
        object.last_modified_by = self.request.user
        object.locked_by_ihub = True
        object.save()
        return super().form_valid(form)


class PersonCreateViewPopout(iHubEditRequiredMixin, CommonPopoutCreateView):
    model = ml_models.Person
    form_class = forms.PersonForm
    h1 = gettext_lazy("New Contact")

    def form_valid(self, form):
        object = form.save(commit=False)
        object.last_modified_by = self.request.user
        object.locked_by_ihub = True
        object.save()
        return super().form_valid(form)


class PersonDeleteView(iHubAdminRequiredMixin, CommonDeleteView):
    model = ml_models.Person
    template_name = 'ihub/confirm_delete.html'
    success_url = reverse_lazy('ihub:person_list')
    home_url_name = "ihub:index"
    grandparent_crumb = {"title": gettext_lazy("Contacts"), "url": reverse_lazy("ihub:person_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("ihub:person_detail", args=[self.get_object().id])}


# ORGANIZATION #
################

class OrganizationListView(iHubBasicMixin, CommonFilterView):
    template_name = 'ihub/organization_list.html'
    filterset_class = filters.OrganizationFilter
    queryset = get_ind_organizations().annotate(
        search_term=Concat(
            'name_eng', Value(" "),
            'abbrev', Value(" "),
            'name_ind', Value(" "),
            'former_name', Value(" "),
            'province__name', Value(" "),
            'province__nom', Value(" "),
            'province__abbrev_eng', Value(" "),
            'province__abbrev_fre', output_field=TextField()))
    paginate_by = 25
    field_list = [
        {"name": 'name_eng', "class": "", "width": ""},
        {"name": 'name_ind', "class": "", "width": ""},
        {"name": 'abbrev', "class": "", "width": ""},
        {"name": 'province', "class": "", "width": ""},
        {"name": 'grouping', "class": "", "width": "200px"},
        {"name": 'full_address|' + str(gettext_lazy("Full address")), "class": "", "width": "300px"},
        {"name": 'Audio recording|{}'.format(gettext_lazy("Audio recording")), "class": "", "width": ""},
    ]
    home_url_name = "ihub:index"
    new_object_url_name = "ihub:org_new"
    row_object_url_name = "ihub:org_detail"
    container_class = "container-fluid"


class OrganizationDetailView(iHubBasicMixin, CommonDetailView):
    model = ml_models.Organization
    template_name = 'ihub/organization_detail.html'
    field_list = [
        'name_eng',
        'name_ind',
        'former_name',
        'abbrev',
        'address',
        'mailing_address',
        'city',
        'postal_code',
        'province',
        'phone',
        'fax',
        'grouping',
        'regions',
        'sectors',
        'dfo_contact_instructions',
        'relationship_rating',
        'orgs',
        'nation',
        'website',
        'council_quorum',
        'next_election',
        'new_coucil_effective_date',
        'election_term',
        'population_on_reserve',
        'population_off_reserve',
        'population_other_reserve',
        'fin',
        'processing_plant',
        'wharf',
        'reserves',
        "metadata|{}".format(gettext_lazy("metadata")),
    ]
    home_url_name = "ihub:index"
    parent_crumb = {"title": gettext_lazy("Organizations"), "url": reverse_lazy("ihub:org_list")}
    container_class = "container-fluid"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # send in a dict with all the entries grouped by status
        org = self.get_object()

        entries_dict = dict()
        if org.entries.exists():
            entries = org.entries.all()
            statuses = models.Status.objects.filter(entries__in=entries).distinct()
            for status in statuses:
                entries_dict[status] = entries.filter(status=status).order_by("initial_date", "title")
        context["entries"] = entries_dict
        return context


class OrganizationUpdateView(iHubEditRequiredMixin, CommonUpdateView):
    model = ml_models.Organization
    template_name = 'ihub/form.html'
    form_class = forms.OrganizationForm
    home_url_name = "ihub:index"
    parent_crumb = {"title": gettext_lazy("Organizations"), "url": reverse_lazy("ihub:org_list")}
    is_multipart_form_data = True

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("ihub:org_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        object = form.save(commit=False)
        object.last_modified_by = self.request.user
        object.locked_by_ihub = True
        super().form_valid(form)
        return HttpResponseRedirect(reverse_lazy('ihub:org_detail', kwargs={'pk': object.id}))


class OrganizationCreateView(iHubEditRequiredMixin, CommonCreateView):
    model = ml_models.Organization
    template_name = 'ihub/form.html'
    form_class = forms.OrganizationForm
    home_url_name = "ihub:index"
    parent_crumb = {"title": gettext_lazy("Organizations"), "url": reverse_lazy("ihub:org_list")}
    is_multipart_form_data = True
    h1 = gettext_lazy("New Organization")

    def form_valid(self, form):
        object = form.save(commit=False)
        object.last_modified_by = self.request.user
        object.locked_by_ihub = True
        super().form_valid(form)
        return HttpResponseRedirect(reverse_lazy('ihub:org_detail', kwargs={'pk': object.id}))


class OrganizationDeleteView(iHubAdminRequiredMixin, CommonDeleteView):
    model = ml_models.Organization
    template_name = 'ihub/confirm_delete.html'
    success_url = reverse_lazy('ihub:org_list')
    home_url_name = "ihub:index"
    parent_crumb = {"title": gettext_lazy("Organizations"), "url": reverse_lazy("ihub:org_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("ihub:org_detail", args=[self.get_object().id])}


# MEMBER  (ORGANIZATION PERSON) #
#################################

class MemberCreateView(iHubEditRequiredMixin, CommonPopoutCreateView):
    model = ml_models.OrganizationMember
    template_name = 'ihub/member_form_popout.html'
    form_class = forms.MemberForm
    width = 1000
    height = 700
    h1 = gettext_lazy("New Organization Member")

    def get_initial(self):
        org = ml_models.Organization.objects.get(pk=self.kwargs['org'])
        return {
            'organization': org,
            'last_modified_by': self.request.user,
        }

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.last_modified_by = self.request.user
        obj = form.save()
        return HttpResponseRedirect(reverse("ihub:member_edit", args=[obj.id]))


class MemberUpdateView(iHubEditRequiredMixin, CommonPopoutUpdateView):
    model = ml_models.OrganizationMember
    template_name = 'ihub/member_form_popout.html'
    form_class = forms.MemberForm
    width = 1000
    height = 800

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.last_modified_by = self.request.user
        return super().form_valid(form)

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
        }


class MemberDeleteView(iHubAdminRequiredMixin, CommonPopoutDeleteView):
    model = ml_models.OrganizationMember


# ENTRY #
#########

class EntryListView(iHubBasicMixin, CommonFilterView):
    template_name = "ihub/entry_list.html"
    model = models.Entry
    filterset_class = filters.EntryFilter
    paginate_by = 100
    field_list = [
        {"name": 'title', "class": "", "width": "400px"},
        {"name": 'entry_type', "class": "", "width": ""},
        {"name": 'regions', "class": "", "width": ""},
        {"name": 'organizations', "class": "", "width": "400px"},
        {"name": 'sectors', "class": "", "width": "200px"},
        {"name": 'status', "class": "", "width": "170px"},
    ]
    new_object_url_name = "ihub:entry_new"
    row_object_url_name = "ihub:entry_detail"
    home_url_name = "ihub:index"
    h1 = gettext_lazy("Entries")
    container_class = "container-fluid"
    open_row_in_new_tab = True


class EntryDetailView(iHubBasicMixin, CommonDetailView):
    model = models.Entry
    home_url_name = "ihub:index"
    parent_crumb = {"title": gettext_lazy("Entries"), "url": reverse_lazy("ihub:entry_list")}
    container_class = "container-fluid"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["field_list"] = [
            'title',
            'proponent',
            'location',
            'organizations',
            'status',
            'is_faa_required',
            'is_faa_issued',
            'sectors',
            'entry_type',
            'initial_date',
            'anticipated_end_date',
            'response_requested_by',
            'regions',
            "metadata|{}".format(gettext_lazy("metadata")),
        ]
        context["field_list_1"] = [
            'fiscal_year',
            'funding_program',
            'funding_needed',
            'funding_purpose',
            'amount_requested',
            'amount_approved',
            'amount_transferred',
            'amount_lapsed',
            'amount_owing'
        ]
        return context


class EntryUpdateView(iHubEditRequiredMixin, CommonUpdateView):
    model = models.Entry
    form_class = forms.EntryForm
    home_url_name = "ihub:index"
    grandparent_crumb = {"title": gettext_lazy("Entries"), "url": reverse_lazy("ihub:entry_list")}
    template_name = "ihub/form.html"

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("ihub:entry_detail", args=[self.get_object().id])}

    def get_initial(self):
        return {'last_modified_by': self.request.user}


class EntryCreateView(iHubEditRequiredMixin, CommonCreateView):
    model = models.Entry
    form_class = forms.EntryCreateForm
    home_url_name = "ihub:index"
    parent_crumb = {"title": gettext_lazy("Entries"), "url": reverse_lazy("ihub:entry_list")}
    template_name = "ihub/form.html"
    h1 = gettext_lazy("New Entry")

    def form_valid(self, form):
        object = form.save()
        models.EntryPerson.objects.create(entry=object, role=1, user_id=self.request.user.id, organization="DFO")

        # create a new email object
        email = emails.NewEntryEmail(object, self.request)
        # send the email object

        custom_send_mail(
            subject=email.subject,
            html_message=email.message,
            from_email=email.from_email,
            recipient_list=email.to_list,
            user=self.request.user
        )
        messages.success(self.request,
                         _("The entry has been submitted and an email has been sent to the Indigenous Hub Coordinator!"))
        return HttpResponseRedirect(reverse_lazy('ihub:entry_detail', kwargs={"pk": object.id}))

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
            'created_by': self.request.user
        }


class EntryDeleteView(iHubAdminRequiredMixin, CommonDeleteView):
    model = models.Entry
    success_url = reverse_lazy('ihub:entry_list')
    home_url_name = "ihub:index"
    grandparent_crumb = {"title": gettext_lazy("Entries"), "url": reverse_lazy("ihub:entry_list")}
    template_name = "ihub/confirm_delete.html"
    delete_protection = False

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse("ihub:entry_detail", args=[self.get_object().id])}


# NOTES #
#########

class NoteCreateView(iHubEditRequiredMixin, CommonPopoutCreateView):
    model = models.EntryNote
    form_class = forms.NoteForm
    width = 700
    height = 750

    def get_initial(self):
        entry = models.Entry.objects.get(pk=self.kwargs['entry'])
        return {
            'author': self.request.user,
            'entry': self.kwargs['entry'],
        }


class NoteUpdateView(iHubEditRequiredMixin, CommonPopoutUpdateView):
    model = models.EntryNote
    form_class = forms.NoteForm
    width = 700
    height = 750


@login_required(login_url='/accounts/login/')
@user_passes_test(in_ihub_edit_group, login_url='/accounts/denied/?app=ihub')
def note_delete(request, pk):
    object = models.EntryNote.objects.get(pk=pk)
    object.delete()
    messages.success(request, _("The note has been successfully deleted from the entry."))
    return HttpResponseRedirect(reverse_lazy("ihub:entry_detail", kwargs={"pk": object.entry.id}))


# ENTRYPERSON #
###############

class EntryPersonCreateView(iHubEditRequiredMixin, CommonPopoutCreateView):
    model = models.EntryPerson
    template_name = 'ihub/entry_person_form_popout.html'
    form_class = forms.EntryPersonForm
    h1 = gettext_lazy("New Entry Person")

    def get_initial(self):
        entry = models.Entry.objects.get(pk=self.kwargs['entry'])
        return {
            'entry': self.kwargs['entry'],
        }


class EntryPersonUpdateView(iHubEditRequiredMixin, CommonPopoutUpdateView):
    model = models.EntryPerson
    template_name = 'ihub/entry_person_form_popout.html'
    form_class = forms.EntryPersonForm


@login_required(login_url='/accounts/login/')
@user_passes_test(in_ihub_edit_group, login_url='/accounts/denied/?app=ihub')
def entry_person_delete(request, pk):
    object = models.EntryPerson.objects.get(pk=pk)
    object.delete()
    messages.success(request, _("The person has been successfully deleted from the entry."))
    return HttpResponseRedirect(reverse_lazy("ihub:entry_detail", kwargs={"pk": object.entry.id}))


# FILE #
########

class FileCreateView(iHubEditRequiredMixin, CommonPopoutCreateView):
    model = models.File
    is_multipart_form_data = True
    form_class = forms.FileForm

    def get_initial(self):
        entry = models.Entry.objects.get(pk=self.kwargs['entry'])
        return {
            'entry': self.kwargs['entry'],
        }


class FileUpdateView(iHubEditRequiredMixin, CommonPopoutUpdateView):
    model = models.File
    is_multipart_form_data = True
    form_class = forms.FileForm


@login_required(login_url='/accounts/login/')
@user_passes_test(in_ihub_edit_group, login_url='/accounts/denied/?app=ihub')
def file_delete(request, pk):
    object = models.File.objects.get(pk=pk)
    object.delete()
    messages.success(request, _("The file has been successfully deleted from the entry."))
    return HttpResponseRedirect(reverse_lazy("ihub:entry_detail", kwargs={"pk": object.entry.id}))


# CONSULTATION INSTRUCTION #
############################

class InstructionCreateView(iHubEditRequiredMixin, CommonPopoutCreateView):
    model = ml_models.ConsultationInstruction
    form_class = forms.InstructionForm

    def get_initial(self):
        org = ml_models.Organization.objects.get(pk=self.kwargs['org'])
        return {
            'organization': org,
            'last_modified_by': self.request.user
        }


class InstructionUpdateView(iHubEditRequiredMixin, CommonPopoutUpdateView):
    model = ml_models.ConsultationInstruction
    form_class = forms.InstructionForm
    template_name = 'ihub/instruction_form.html'

    def get_initial(self):
        return {
            'last_modified_by': self.request.user
        }


class InstructionDeleteView(iHubAdminRequiredMixin, CommonPopoutDeleteView):
    model = ml_models.ConsultationInstruction


# Consultation Role #
#####################

class ConsultationRoleCreateView(iHubEditRequiredMixin, CommonPopoutCreateView):
    model = ml_models.ConsultationRole
    form_class = forms.ConsultationRoleForm

    def get_initial(self):
        return {
            'organization': self.kwargs['organization'],
            'member': self.kwargs['member'],
            'last_modified_by': self.request.user,
        }

    def form_valid(self, form):
        obj = form.save()
        return HttpResponseRedirect(reverse("ihub:member_edit", args=[obj.member.id]))


class ConsultationRoleUpdateView(iHubEditRequiredMixin, CommonPopoutUpdateView):
    model = ml_models.ConsultationRole
    form_class = forms.ConsultationRoleForm

    def get_initial(self):
        return {
            'last_modified_by': self.request.user,
        }

    def get_success_url(self):
        return reverse("ihub:member_edit", args=[self.get_object().member.id])


class ConsultationRoleDeleteView(iHubAdminRequiredMixin, CommonPopoutDeleteView):
    model = ml_models.ConsultationRole

    def get_success_url(self):
        return reverse("ihub:member_edit", args=[self.get_object().member.id])


# REPORTS #
###########

class ReportSearchFormView(iHubBasicMixin, FormView):
    template_name = 'ihub/report_search.html'
    form_class = forms.ReportSearchForm

    def get_initial(self):
        return {"report_title": _("Activity Log – Government of Canada")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        sectors = listrify(form.cleaned_data["sectors"])
        orgs = listrify(form.cleaned_data["organizations"])
        orgs_w_consultation_instructions = listrify(form.cleaned_data["orgs_w_consultation_instructions"])
        statuses = listrify(form.cleaned_data["statuses"])
        entry_types = listrify(form.cleaned_data["entry_types"])
        org = int(nz(form.cleaned_data["single_org"]), 0)
        # fy = str(form.cleaned_data["fiscal_year"])
        report_title = str(form.cleaned_data["report_title"])
        report = int(form.cleaned_data["report"])
        format = str(form.cleaned_data["format"])
        from_date = nz(form.cleaned_data["from_date"], "None")
        to_date = nz(form.cleaned_data["to_date"], "None")
        entry_note_types = listrify(form.cleaned_data["entry_note_types"])
        entry_note_types_all = listrify(form.cleaned_data["entry_note_types_all"])
        entry_note_statuses = listrify(form.cleaned_data["entry_note_statuses"])
        org_regions = listrify(form.cleaned_data["org_regions"])
        entry_regions = listrify(form.cleaned_data["entry_regions"])

        if report == 1:  # capacity report
            qry = f'?sectors={nz(sectors, "None")}&' \
                  f'from_date={nz(from_date, "None")}&' \
                  f'to_date={nz(to_date, "None")}&' \
                  f'orgs={nz(orgs, "None")}'
            return HttpResponseRedirect(reverse("ihub:capacity_xlsx") + qry)

        elif report == 2:
            return HttpResponseRedirect(reverse("ihub:report_q", kwargs={"org": org}))

        elif report == 3:
            qry = f'?sectors={nz(sectors, "None")}&' \
                  f'from_date={nz(from_date, "None")}&' \
                  f'to_date={nz(to_date, "None")}&' \
                  f'orgs={nz(orgs, "None")}&' \
                  f'entry_note_types={nz(entry_note_types, "None")}&' \
                  f'entry_note_statuses={nz(entry_note_statuses, "None")}'
            if format == 'pdf':
                return HttpResponseRedirect(reverse("ihub:summary_pdf") + qry)
            else:
                return HttpResponseRedirect(reverse("ihub:summary_xlsx") + qry)

        elif report == 6:  # Engagement Update Log
            qry = f'?sectors={nz(sectors, "None")}&' \
                  f'from_date={nz(from_date, "None")}&' \
                  f'to_date={nz(to_date, "None")}&' \
                  f'orgs={nz(orgs, "None")}&' \
                  f'statuses={nz(statuses, "None")}&' \
                  f'entry_types={nz(entry_types, "None")}&' \
                  f'report_title={nz(report_title, "None")}&' \
                  f'entry_note_types={nz(entry_note_types, "None")}&' \
                  f'entry_note_statuses={nz(entry_note_statuses, "None")}'
            if format == 'pdf':
                return HttpResponseRedirect(reverse("ihub:consultation_log_pdf") + qry)
            else:
                return HttpResponseRedirect(reverse("ihub:consultation_log_xlsx") + qry)

        elif report == 7:
            return HttpResponseRedirect(
                f'{reverse("ihub:consultation_instructions_pdf")}?orgs={orgs_w_consultation_instructions}'
            )
        elif report == 8:
            return HttpResponseRedirect(
                f'{reverse("ihub:consultation_instructions_xlsx")}?orgs={orgs_w_consultation_instructions}'
            )
        elif report == 9:  # Engagement Update Log
            qry = f'?sectors={nz(sectors, "None")}&' \
                  f'from_date={nz(from_date, "None")}&' \
                  f'to_date={nz(to_date, "None")}&' \
                  f'orgs={nz(orgs, "None")}&' \
                  f'statuses={nz(statuses, "None")}&' \
                  f'entry_note_types={nz(entry_note_types_all, "None")}&' \
                  f'entry_note_statuses={nz(entry_note_statuses, "None")}&' \
                  f'org_regions={nz(org_regions, "None")}&' \
                  f'entry_regions={nz(entry_regions, "None")}'
            return HttpResponseRedirect(reverse("ihub:consultation_report") + qry)

        else:
            messages.error(self.request, "Report is not available. Please select another report.")
            return HttpResponseRedirect(reverse("ihub:report_search"))


def capacity_export_spreadsheet(request):
    sectors = request.GET["sectors"]
    orgs = request.GET["orgs"]
    from_date = request.GET["from_date"]
    to_date = request.GET["to_date"]

    file_url = reports.generate_capacity_spreadsheet(orgs, sectors, from_date, to_date)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="iHub Capacity Report ({}).xlsx"'.format(
                timezone.now().strftime("%Y-%m-%d"))
            return response
    raise Http404


def summary_export_spreadsheet(request):
    sectors = request.GET["sectors"]
    orgs = request.GET["orgs"]
    from_date = request.GET["from_date"]
    to_date = request.GET["to_date"]
    entry_note_types = request.GET["entry_note_types"]
    entry_note_statuses = request.GET["entry_note_statuses"]

    file_url = reports.generate_summary_spreadsheet(orgs, sectors, from_date, to_date, entry_note_types, entry_note_statuses)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="iHub Summary Report ({}).xlsx"'.format(timezone.now().strftime("%Y-%m-%d"))
            return response
    raise Http404


def consultation_log_export_spreadsheet(request):
    # first, filter out the "none" placeholder
    sectors = request.GET["sectors"]
    orgs = request.GET["orgs"]
    statuses = request.GET["statuses"]
    entry_types = request.GET["entry_types"]
    report_title = request.GET["report_title"]
    from_date = request.GET["from_date"]
    to_date = request.GET["to_date"]
    entry_note_types = request.GET["entry_note_types"]
    entry_note_statuses = request.GET["entry_note_statuses"]

    file_url = reports.generate_consultation_log_spreadsheet(orgs, sectors, statuses, entry_types, report_title, from_date, to_date,
                                                             entry_note_types, entry_note_statuses)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="Engagement Update Log ({}).xlsx"'.format(
                timezone.now().strftime("%Y-%m-%d"))
            return response
    raise Http404


def consultation_report(request):
    # first, filter out the "none" placeholder
    sectors = request.GET["sectors"]
    orgs = request.GET["orgs"]
    statuses = request.GET["statuses"]
    from_date = request.GET["from_date"]
    to_date = request.GET["to_date"]
    entry_note_types = request.GET["entry_note_types"]
    entry_note_statuses = request.GET["entry_note_statuses"]
    org_regions = request.GET["org_regions"]
    entry_regions = request.GET["entry_regions"]

    file_url = reports.generate_consultation_report(orgs, sectors, statuses, from_date, to_date, entry_note_types, entry_note_statuses, org_regions,
                                                    entry_regions)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename="Consultation Report ({}).xlsx"'.format(
                timezone.now().strftime("%Y-%m-%d"))
            return response
    raise Http404


class OrganizationCueCard(PDFTemplateView):
    template_name = "ihub/report_cue_card.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org = ml_models.Organization.objects.get(pk=self.kwargs["org"])
        context["org"] = org

        context["org_field_list_1"] = [
            'name_eng',
            'name_ind',
            'former_name',
            'abbrev',
            'nation',
            'website',
        ]
        context["org_field_list_2"] = [
            'address',
            'mailing_address',
            'city',
            'postal_code',
            'province',
            'phone',
            'fax',
        ]
        context["org_field_list_3"] = [
            'next_election',
            'election_term',
            'new_coucil_effective_date',
            'population_on_reserve',
            'population_off_reserve',
            'population_other_reserve',
            'relationship_rating',
        ]
        context["org_field_list_4"] = [
            'fin',
            'processing_plant',
            'wharf',
            'dfo_contact_instructions',
            'council_quorum',
            'reserves',
            'orgs',
            'notes',
        ]

        # determine how many rows for the table
        context["contact_table_rows"] = range(0, math.ceil(org.members.count() / 4))
        context["one_to_four"] = range(0, 4)

        context["entry_field_list_1"] = [
            'fiscal_year',
            'initial_date',
            'anticipated_end_date',
            'status',
        ]
        context["entry_field_list_2"] = [
            'sectors',
            'entry_type',
            'regions',
        ]
        context["entry_field_list_3"] = [
            'funding_program',
            'funding_needed',
            'funding_purpose',
            'amount_requested',
        ]
        context["entry_field_list_4"] = [
            'amount_approved',
            'amount_transferred',
            'amount_lapsed',
        ]
        context["entry_field_list_5"] = [
            'amount_owing',
        ]
        context["now"] = timezone.now()
        return context


class PDFSummaryReport(PDFTemplateView):
    template_name = "ihub/report_pdf_summary.html"

    def get_pdf_filename(self):
        pdf_filename = "iHub Summary Report ({}).pdf".format(timezone.now().strftime("%Y-%m-%d"))
        return pdf_filename

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get an entry list for the fiscal year (if any)

        # first, filter out the "none" placeholder
        sectors = self.request.GET["sectors"]
        orgs = self.request.GET["orgs"]
        from_date = self.request.GET["from_date"]
        to_date = self.request.GET["to_date"]
        entry_note_types = self.request.GET["entry_note_types"]
        entry_note_statuses = self.request.GET["entry_note_statuses"]

        if sectors == "None":
            sectors = None
        if orgs == "None":
            orgs = None
        if from_date == "None":
            from_date = None
        if to_date == "None":
            to_date = None
        if entry_note_types == "None":
            entry_note_types = None
        else:
            entry_note_types = [int(i) for i in entry_note_types.split(",")] if entry_note_types else None

        if entry_note_statuses == "None":
            entry_note_statuses = None
        else:
            entry_note_statuses = [int(i) for i in entry_note_statuses.split(",")] if entry_note_statuses else None

        # get an entry list for the fiscal year (if any)
        entry_list = models.Entry.objects.all()

        if sectors:
            # we have to refine the queryset to only the selected sectors
            sector_list = [ml_models.Sector.objects.get(pk=int(s)) for s in sectors.split(",")]
            entry_list = entry_list.filter(sectors__in=sector_list)
        if orgs:
            # we have to refine the queryset to only the selected orgs
            org_list = [ml_models.Organization.objects.get(pk=int(o)) for o in orgs.split(",")]
            entry_list = entry_list.filter(organizations__in=org_list)

        if from_date or to_date:
            id_list = []
            d0_start = datetime.strptime(from_date, "%Y-%m-%d").replace(tzinfo=timezone.get_current_timezone()) if from_date else None
            d0_end = datetime.strptime(to_date, "%Y-%m-%d").replace(tzinfo=timezone.get_current_timezone()) if to_date else None
            for e in entry_list:
                d1_start = e.initial_date
                d1_end = e.anticipated_end_date
                if get_date_range_overlap(d0_start, d0_end, d1_start, d1_end) > 0:
                    id_list.append(e.id)
            entry_list = entry_list.filter(id__in=id_list)

        entry_list.distinct()

        context["entry_list"] = entry_list

        # remove any orgs without entries
        org_list = list(set([org for entry in entry_list for org in entry.organizations.all()]))

        # create a queryset
        if len(org_list) > 0:
            org_id_list = [o.id for o in org_list]
            org_list = ml_models.Organization.objects.filter(id__in=org_id_list).order_by("abbrev")

        context["org_list"] = org_list

        # create a dict for the index page
        my_dict = {}
        for org in org_list:
            my_dict[org.id] = entry_list.filter(organizations=org).order_by("title")
        context["my_dict"] = my_dict

        context["field_list"] = [
            'title',
            'location',
            'organizations',
            'status',
            'sectors',
            'entry_type',
            'initial_date',
            'anticipated_end_date',
            'regions',
            'created_by',
        ]

        context["field_list_1"] = [
            'fiscal_year',
            'funding_program',
            'funding_needed',
            'funding_purpose',
            'amount_requested',
            'amount_approved',
            'amount_transferred',
            'amount_lapsed',
            'amount_owing'
        ]
        context["entry_note_types"] = entry_note_types
        context["entry_note_statuses"] = entry_note_statuses

        return context


class ConsultationLogPDFTemplateView(TemplateView):
    template_name = "ihub/report_consultation_log.html"

    # def get_pdf_filename(self):
    #     pdf_filename = "Consultations Update Log ({}).pdf".format(timezone.now().strftime("%Y-%m-%d"))
    #     return pdf_filename

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get an entry list for the fiscal year (if any)

        # first, filter out the "none" placeholder
        sectors = self.request.GET["sectors"]
        orgs = self.request.GET["orgs"]
        statuses = self.request.GET["statuses"]
        entry_types = self.request.GET["entry_types"]
        report_title = self.request.GET["report_title"]
        from_date = self.request.GET["from_date"]
        to_date = self.request.GET["to_date"]
        entry_note_types = self.request.GET["entry_note_types"]
        entry_note_statuses = self.request.GET["entry_note_statuses"]

        if sectors == "None":
            sectors = None
        if orgs == "None":
            orgs = None
        if statuses == "None":
            statuses = None
        if entry_types == "None":
            entry_types = None
        if from_date == "None":
            from_date = None
        if to_date == "None":
            to_date = None
        if entry_note_types == "None":
            entry_note_types = None
        else:
            entry_note_types = [int(i) for i in entry_note_types.split(",")] if entry_note_types else None

        if entry_note_statuses == "None":
            entry_note_statuses = None
        else:
            entry_note_statuses = [int(i) for i in entry_note_statuses.split(",")] if entry_note_statuses else None

        # get an entry list for the fiscal year (if any)
        entry_list = models.Entry.objects.all().order_by("status", "-initial_date")

        if orgs:
            # we have to refine the queryset to only the selected orgs
            org_list = [ml_models.Organization.objects.get(pk=int(o)) for o in orgs.split(",")]
            entry_list = entry_list.filter(organizations__in=org_list)

        if sectors:
            # we have to refine the queryset to only the selected sectors
            sector_list = [ml_models.Sector.objects.get(pk=int(s)) for s in sectors.split(",")]
            entry_list = entry_list.filter(sectors__in=sector_list)

        if statuses:
            # we have to refine the queryset to only the selected statuses
            status_list = [models.Status.objects.get(pk=int(o)) for o in statuses.split(",")]
            entry_list = entry_list.filter(status__in=status_list)

        if entry_types:
            # we have to refine the queryset to only the selected orgs
            entry_type_list = [models.EntryType.objects.get(pk=int(o)) for o in entry_types.split(",")]
            entry_list = entry_list.filter(entry_type__in=entry_type_list).distinct()

        if from_date or to_date:
            id_list = []
            d0_start = datetime.strptime(from_date, "%Y-%m-%d").replace(tzinfo=timezone.get_current_timezone()) if from_date else None
            d0_end = datetime.strptime(to_date, "%Y-%m-%d").replace(tzinfo=timezone.get_current_timezone()) if to_date else None
            for e in entry_list:
                d1_start = e.initial_date
                d1_end = e.anticipated_end_date
                if get_date_range_overlap(d0_start, d0_end, d1_start, d1_end) > 0:
                    id_list.append(e.id)
            entry_list = entry_list.filter(id__in=id_list)

        context["entry_list"] = entry_list
        context["entry_note_types"] = entry_note_types
        context["entry_note_statuses"] = entry_note_statuses
        context["report_title"] = report_title

        return context


class ReportConsultationInstructionsPDFView(PDFTemplateView):
    template_name = 'ihub/report_consultation_instructions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        orgs = self.request.GET["orgs"] if self.request.GET.get("orgs") else "None"
        orgs = None if orgs == "None" else orgs

        # if there are some organizations that are specified,
        if orgs:
            # we have to refine the queryset to only the selected orgs
            object_list = ml_models.ConsultationInstruction.objects.filter(organization_id__in=orgs.split(","))
        else:
            # else return all orgs
            object_list = ml_models.ConsultationInstruction.objects.all()
        context["object_list"] = object_list
        context["now"] = timezone.now()
        # now we need to refine the list again to only
        return context


def consultation_instructions_export_spreadsheet(request):
    orgs = request.GET["orgs"] if request.GET.get("orgs") else "None"
    file_url = reports.consultation_instructions_export_spreadsheet(orgs)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; ' \
                                              f'filename="iHub Consultation Instructions Export ({timezone.now().strftime("%Y-%m-%d")}).xlsx"'
            return response
    raise Http404


# SETTINGS #
############


class OrganizationFormsetView(iHubAdminRequiredMixin, CommonFormsetView):
    template_name = 'ihub/organization_formset.html'
    h1 = "Manage Organizations"
    queryset = get_ind_organizations()
    formset_class = forms.OrganizationFormSet
    success_url_name = "ihub:manage_orgs"
    home_url_name = "ihub:index"
    container_class = "container-fluid"


class SectorFormsetView(iHubAdminRequiredMixin, CommonFormsetView):
    template_name = 'ihub/formset.html'
    h1 = "Manage Sectors"
    queryset = ml_models.Sector.objects.all()
    formset_class = forms.SectorFormSet
    success_url_name = "ihub:manage_sectors"
    home_url_name = "ihub:index"
    delete_url_name = "ihub:delete_sector"


class SectorHardDeleteView(iHubAdminRequiredMixin, CommonHardDeleteView):
    model = ml_models.Sector
    success_url = reverse_lazy("ihub:manage_sectors")


class StatusFormsetView(iHubAdminRequiredMixin, CommonFormsetView):
    template_name = 'ihub/formset.html'
    h1 = "Manage Statuses"
    queryset = models.Status.objects.all()
    formset_class = forms.StatusFormSet
    success_url_name = "ihub:manage_statuses"
    home_url_name = "ihub:index"
    delete_url_name = "ihub:delete_status"


class StatusHardDeleteView(iHubAdminRequiredMixin, CommonHardDeleteView):
    model = models.Status
    success_url = reverse_lazy("ihub:manage_statuses")


class EntryTypeFormsetView(iHubAdminRequiredMixin, CommonFormsetView):
    template_name = 'ihub/formset.html'
    h1 = "Manage Entry Types"
    queryset = models.EntryType.objects.all()
    formset_class = forms.EntryTypeFormSet
    success_url_name = "ihub:manage_entry_types"
    home_url_name = "ihub:index"
    delete_url_name = "ihub:delete_entry_type"


class EntryTypeHardDeleteView(iHubAdminRequiredMixin, CommonHardDeleteView):
    model = models.EntryType
    success_url = reverse_lazy("ihub:manage_entry_types")


class FundingPurposeFormsetView(iHubAdminRequiredMixin, CommonFormsetView):
    template_name = 'ihub/formset.html'
    h1 = "Manage Funding Purposes"
    queryset = models.FundingPurpose.objects.all()
    formset_class = forms.FundingPurposeFormSet
    success_url_name = "ihub:manage_funding_purposes"
    home_url_name = "ihub:index"
    delete_url_name = "ihub:delete_funding_purpose"


class FundingPurposeHardDeleteView(iHubAdminRequiredMixin, CommonHardDeleteView):
    model = models.FundingPurpose
    success_url = reverse_lazy("ihub:manage_funding_purposes")


class ReserveFormsetView(iHubAdminRequiredMixin, CommonFormsetView):
    template_name = 'ihub/formset.html'
    h1 = "Manage Reserves"
    queryset = ml_models.Reserve.objects.all()
    formset_class = forms.ReserveFormSet
    success_url_name = "ihub:manage_reserves"
    home_url_name = "ihub:index"
    delete_url_name = "ihub:delete_reserve"


class ReserveHardDeleteView(iHubAdminRequiredMixin, CommonHardDeleteView):
    model = ml_models.Reserve
    success_url = reverse_lazy("ihub:manage_reserves")


class GroupingFormsetView(iHubAdminRequiredMixin, CommonFormsetView):
    template_name = 'ihub/formset.html'
    h1 = "Manage Groupings"
    queryset = ml_models.Grouping.objects.all()
    formset_class = forms.GroupingFormSet
    success_url_name = "ihub:manage_groupings"
    home_url_name = "ihub:index"
    delete_url_name = "ihub:delete_grouping"


class GroupingHardDeleteView(iHubAdminRequiredMixin, CommonHardDeleteView):
    model = ml_models.Grouping
    success_url = reverse_lazy("ihub:manage_groupings")


class NationFormsetView(iHubAdminRequiredMixin, CommonFormsetView):
    template_name = 'ihub/formset.html'
    h1 = "Manage Nations"
    queryset = ml_models.Nation.objects.all()
    formset_class = forms.NationFormSet
    success_url_name = "ihub:manage_nations"
    home_url_name = "ihub:index"
    delete_url_name = "ihub:delete_nation"


class NationHardDeleteView(iHubAdminRequiredMixin, CommonHardDeleteView):
    model = ml_models.Nation
    success_url = reverse_lazy("ihub:manage_nations")


class FundingProgramFormsetView(iHubAdminRequiredMixin, CommonFormsetView):
    template_name = 'ihub/formset.html'
    h1 = "Manage Funding Programs"
    queryset = models.FundingProgram.objects.all()
    formset_class = forms.FundingProgramFormSet
    success_url_name = "ihub:manage_programs"
    home_url_name = "ihub:index"
    delete_url_name = "ihub:delete_program"


class FundingProgramHardDeleteView(iHubAdminRequiredMixin, CommonHardDeleteView):
    model = models.FundingProgram
    success_url = reverse_lazy("ihub:manage_programs")


class RelationshipRatingFormsetView(iHubAdminRequiredMixin, CommonFormsetView):
    template_name = 'ihub/formset.html'
    h1 = "Manage Relationship Ratings"
    queryset = ml_models.RelationshipRating.objects.all()
    formset_class = forms.RelationshipRatingFormSet
    success_url_name = "ihub:manage_ratings"
    home_url_name = "ihub:index"
    delete_url_name = "ihub:delete_rating"


class RelationshipRatingHardDeleteView(iHubAdminRequiredMixin, CommonHardDeleteView):
    model = ml_models.RelationshipRating
    success_url = reverse_lazy("ihub:manage_ratings")


class iHubUserFormsetView(SuperuserOrAdminRequiredMixin, CommonFormsetView):
    template_name = 'ihub/formset.html'
    h1 = "Manage iHub Users"
    queryset = models.iHubUser.objects.all()
    formset_class = forms.iHubUserFormset
    success_url_name = "ihub:manage_ihub_users"
    home_url_name = "ihub:index"
    delete_url_name = "ihub:delete_ihub_user"
    container_class = "container bg-light curvy"


class iHubUserHardDeleteView(SuperuserOrAdminRequiredMixin, CommonHardDeleteView):
    model = models.iHubUser
    success_url = reverse_lazy("ihub:manage_ihub_users")

