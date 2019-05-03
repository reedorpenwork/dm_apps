from django import forms
from django.forms import modelformset_factory
from django.utils.translation import gettext as _
from shared_models import models as shared_models
from masterlist import models as ml_models
from . import models

YES_NO_CHOICES = (
    (True, _("Yes")),
    (False, _("No")),
)


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = ml_models.Organization
        fields = [
            'name_eng',
            'abbrev',
            'address',
            'city',
            'postal_code',
            'province',
            'phone',
            'fax',
            'dfo_contact_instructions',
            'notes',
            'grouping',
            'regions',
            'sectors',
            'last_modified_by',
        ]
        widgets = {
            'key_species': forms.Textarea(attrs={"rows": 2}),
            'dfo_contact_instructions': forms.Textarea(attrs={"rows": 2}),
            'notes': forms.Textarea(attrs={"rows": 2}),
            'last_modified_by': forms.HiddenInput(),
        }


class NewMemberForm(forms.ModelForm):
    class Meta:
        model = ml_models.OrganizationMember
        fields = [
            'person',
            'organization',
            'role',
            'notes',
            'last_modified_by',
        ]
        widgets = {
            'organization': forms.HiddenInput(),
            'notes': forms.Textarea(attrs={"rows": 2}),
            'last_modified_by': forms.HiddenInput(),
        }


class MemberForm(forms.ModelForm):
    class Meta:
        model = ml_models.OrganizationMember
        fields = [
            'person',
            'organization',
            'role',
            'notes',
            'last_modified_by',
        ]
        widgets = {
            'notes': forms.Textarea(attrs={"rows": 2}),
            'organization': forms.HiddenInput(),
            'last_modified_by': forms.HiddenInput(),
        }
        labels = {
            'notes': _("Additional notes about member"),
        }


class PersonForm(forms.ModelForm):
    class Meta:
        model = ml_models.Person
        exclude = ["date_last_modified", ]

        widgets = {
            'last_modified_by': forms.HiddenInput(),
            'notes': forms.Textarea(attrs={"rows": 3}),
        }
#
#

# class InstructionForm(forms.ModelForm):
#     class Meta:
#         model = models.ConsultationInstruction
#         exclude = [
#             'date_last_modified',
#         ]
#         widgets = {
#             'organization': forms.HiddenInput(),
#             'notes': forms.Textarea(attrs={"rows": 3}),
#             'last_modified_by': forms.HiddenInput(),
#         }
#
#
# class RecipientForm(forms.ModelForm):
#     class Meta:
#         model = models.ConsultationInstructionRecipient
#         exclude = ["date_last_modified"]
#         widgets = {
#             'member': forms.HiddenInput(),
#             'consultation_instruction': forms.HiddenInput(),
#             'last_modified_by': forms.HiddenInput(),
#         }
#
#
# class OrganizationFormShort(forms.ModelForm):
#     class Meta:
#         model = models.Organization
#         fields = [
#             'name_eng',
#             'name_fre',
#             'name_ind',
#             'abbrev',
#             'address',
#             'city',
#             'postal_code',
#             'province',
#             'phone',
#             'fax',
#             'next_election',
#             'election_term',
#             'population_on_reserve',
#             'population_off_reserve',
#             'population_other_reserve',
#             'fin',
#             'notes',
#             'grouping',
#         ]
#         widgets = {
#             'notes': forms.Textarea(attrs={"rows": 2}),
#         }
#
#
# OrganizationFormSet = modelformset_factory(
#     model=models.Organization,
#     form=OrganizationFormShort,
#     extra=1,
# )
#
#
# class RegionForm(forms.ModelForm):
#     class Meta:
#         model = shared_models.Region
#         fields = "__all__"
#
#
# RegionFormSet = modelformset_factory(
#     model=shared_models.Region,
#     form=RegionForm,
#     extra=1,
# )
#
#
# class GroupingForm(forms.ModelForm):
#     class Meta:
#         model = models.Grouping
#         fields = "__all__"
#
#
# GroupingFormSet = modelformset_factory(
#     model=models.Grouping,
#     form=GroupingForm,
#     extra=1,
# )
#
#
# class ReportSearchForm(forms.Form):
#
#     REPORT_CHOICES = (
#         (None, "------"),
#         (1, "Master list custom export (xlsx)"),
#     )
#
#     report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
#
#     # report #1
#     is_indigenous = forms.BooleanField(required=False, label=_('Indigenous Only'))
#     species = forms.CharField(required=False, label=_('Key Species'))
#
#     field_order = ["provinces","groupings","sectors","regions","is_indigenous","species"]
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         province_choices = [(obj.id, str(obj)) for obj in shared_models.Province.objects.all()]
#         grouping_choices = [(obj.id, str(obj)) for obj in models.Grouping.objects.all()]
#         sector_choices = [(obj.id, str(obj)) for obj in models.Sector.objects.all()]
#         region_choices = [(obj.id, str(obj)) for obj in shared_models.Region.objects.all()]
#
#         self.fields["provinces"] = forms.MultipleChoiceField(required=False, choices=province_choices,
#                                           label=_('Provinces - Leave blank for all'))
#         self.fields["groupings"] = forms.MultipleChoiceField(required=False, choices=grouping_choices,
#                                           label=_('Organization Grouping - Leave blank for all'))
#         self.fields["sectors"] = forms.MultipleChoiceField(required=False, choices=sector_choices,
#                                         label=_('DFO Sectors - Leave blank for all'))
#         self.fields["regions"] = forms.MultipleChoiceField(required=False, choices=region_choices,
#                                         label=_('DFO Regions - Leave blank for all'))