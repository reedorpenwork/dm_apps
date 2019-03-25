from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from shared_models import models as shared_models
from . import models


class ResponsibilityCentreForm(forms.ModelForm):
    class Meta:
        model = shared_models.ResponsibilityCenter
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        USER_CHOICES = [(u.id, "{}, {}".format(u.last_name, u.first_name)) for u in
                        User.objects.all().order_by("last_name", "first_name")]
        USER_CHOICES.insert(0, tuple((None, "---")))

        super().__init__(*args, **kwargs)
        self.fields['manager'].choices = USER_CHOICES


class LineObjectForm(forms.ModelForm):
    class Meta:
        model = shared_models.LineObject
        fields = "__all__"


class BusinessLineForm(forms.ModelForm):
    class Meta:
        model = shared_models.BusinessLine
        fields = "__all__"


class AllotmentCodeForm(forms.ModelForm):
    class Meta:
        model = shared_models.AllotmentCode
        fields = "__all__"


class ProjectForm(forms.ModelForm):
    class Meta:
        model = shared_models.Project
        fields = "__all__"


class TransactionForm(forms.ModelForm):
    do_another = forms.IntegerField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = models.Transaction
        exclude = ["outstanding_obligation"]
        labels = {
            "fiscal_year": "Fiscal year (SAP style e.g. 2018-2019 = 2019)",
        }
        widgets = {
            "fiscal_year": forms.NumberInput(),
            "created_by": forms.HiddenInput(),
            "creation_date": forms.DateInput(attrs={"type": "date"}),
            "invoice_date": forms.DateInput(attrs={"type": "date"}),
        }


class CustomTransactionForm(forms.ModelForm):
    do_another = forms.IntegerField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = models.Transaction
        fields = [
            "project",
            "responsibility_center",
            "business_line",
            "allotment_code",
            "line_object",
            "supplier_description",
            "obligation_cost",
            "reference_number",
            "comment",

            # hidden fields
            "created_by",
            "creation_date",
            "transaction_type",
            "in_mrs",
        ]

        labels = {
            "supplier_description": "Expense description",
            "obligation_cost": "Cost estimation",
        }

        widgets = {
            "comment": forms.Textarea(attrs={"rows": 4}),

            # hidden because they are given default values
            "created_by": forms.HiddenInput(),
            "creation_date": forms.HiddenInput(),
            "transaction_type": forms.HiddenInput(),
            "in_mrs": forms.HiddenInput(),
        }


class ReportSearchForm(forms.Form):
    FY_CHOICES = [(obj.id, "{}".format(obj.full)) for obj in shared_models.FiscalYear.objects.all()]
    FY_CHOICES.insert(0, (None, "------"))
    RC_CHOICES = [(obj.id, obj) for obj in shared_models.ResponsibilityCenter.objects.all()]
    RC_CHOICES.insert(0, (None, "------"))
    PROJECT_CHOICES = [(obj.id, "{} - {}".format(obj.code, obj.name)) for obj in shared_models.Project.objects.all()]
    PROJECT_CHOICES.insert(0, (None, "------"))
    REPORT_CHOICES = [
        # (1, "Branch Summary"),
        (2, "RC Summary"),
        (3, "Project Summary"),
    ]
    REPORT_CHOICES.insert(0, (None, "------"))

    report = forms.ChoiceField(required=True, choices=REPORT_CHOICES)
    fiscal_year = forms.ChoiceField(required=True, choices=FY_CHOICES)
    rc = forms.ChoiceField(required=False, choices=RC_CHOICES, label="Responsibility centre")
    project = forms.ChoiceField(required=False, choices=PROJECT_CHOICES, label="Project")
