import csv
from copy import deepcopy
from datetime import date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User, Group
from django.db.models import TextField, Value
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.utils.translation.trans_null import gettext_lazy
from django.views.generic import TemplateView

from shared_models.views import CommonPopoutFormView, CommonListView, CommonFilterView, CommonDetailView, \
    CommonDeleteView, CommonCreateView, CommonUpdateView, CommonPopoutUpdateView, CommonPopoutDeleteView, \
    CommonFormView, CommonHardDeleteView, CommonFormsetView, CommonPopoutCreateView
from . import filters
from . import forms
from . import models, emails
from .models import TransactionCategory, Location


class CloserTemplateView(TemplateView):
    template_name = 'whalebrary/close_me.html'


### Permissions ###

class WhalebraryAccessRequired(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return True

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/?app=whalebrary')
        return super().dispatch(request, *args, **kwargs)


def in_whalebrary_admin_group(user):
    if "whalebrary_admin" in [g.name for g in user.groups.all()]:
        return True


class WhalebraryAdminAccessRequired(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return in_whalebrary_admin_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/?app=whalebrary')
        return super().dispatch(request, *args, **kwargs)


def in_whalebrary_edit_group(user):
    """this group includes the admin group so there is no need to add an admin to this group"""
    if user:
        if in_whalebrary_admin_group(user) or user.groups.filter(name='whalebrary_edit').count() != 0:
            return True


class WhalebraryEditRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return in_whalebrary_edit_group(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/?app=whalebrary')
        return super().dispatch(request, *args, **kwargs)


@login_required(login_url='/accounts/login/')
def index(request):
    return render(request, 'whalebrary/index.html')


@login_required(login_url='/accounts/login/')
@user_passes_test(in_whalebrary_admin_group, login_url='/accounts/denied/?app=whalebrary')
def admin_tools(request):
    return render(request, 'whalebrary/_admin.html')

## ADMIN USER ACCESS CONTROL ##


class UserListView(WhalebraryAdminAccessRequired, CommonFilterView):
    template_name = "whalebrary/user_list.html"
    filterset_class = filters.UserFilter
    home_url_name = "index"
    paginate_by = 25
    h1 = "Whalebrary App User List"
    field_list = [
        {"name": 'first_name', "class": "", "width": ""},
        {"name": 'last_name', "class": "", "width": ""},
        {"name": 'email', "class": "", "width": ""},
        {"name": 'last_login|{}'.format(gettext_lazy("Last login to DM Apps")), "class": "", "width": ""},
    ]
    new_object_url = reverse_lazy("shared_models:user_new")

    def get_queryset(self):
        queryset = User.objects.order_by("first_name", "last_name").annotate(
            search_term=Concat('first_name', Value(""), 'last_name', Value(""), 'email', output_field=TextField())
        )
        if self.kwargs.get("whalebrary"):
            queryset = queryset.filter(groups__name__icontains="whalebrary").distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["whalebrary_admin"] = get_object_or_404(Group, name="whalebrary_admin")
        context["whalebrary_edit"] = get_object_or_404(Group, name="whalebrary_edit")
        return context


@login_required(login_url='/accounts/login/')
@user_passes_test(in_whalebrary_admin_group, login_url='/accounts/denied/?app=whalebrary')
def toggle_user(request, pk, type):
    my_user = User.objects.get(pk=pk)
    whalebrary_admin = get_object_or_404(Group, name="whalebrary_admin")
    whalebrary_edit = get_object_or_404(Group, name="whalebrary_edit")
    if type == "admin":
        # if the user is in the admin group, remove them
        if whalebrary_admin in my_user.groups.all():
            my_user.groups.remove(whalebrary_admin)
        # otherwise add them
        else:
            my_user.groups.add(whalebrary_admin)
    elif type == "edit":
        # if the user is in the edit group, remove them
        if whalebrary_edit in my_user.groups.all():
            my_user.groups.remove(whalebrary_edit)
        # otherwise add them
        else:
            my_user.groups.add(whalebrary_edit)
    return HttpResponseRedirect("{}#user_{}".format(request.META.get('HTTP_REFERER'), my_user.id))


## ADMIN FORMSETS ##

## LOCATION ##


class LocationHardDeleteView(WhalebraryAdminAccessRequired, CommonHardDeleteView):
    model = models.Location
    success_url = reverse_lazy("whalebrary:manage_locations")


class LocationFormsetView(WhalebraryAdminAccessRequired, CommonFormsetView):
    template_name = 'whalebrary/formset.html'
    h1 = "Manage Locations"
    queryset = models.Location.objects.all()
    formset_class = forms.LocationFormset
    success_url = reverse_lazy("whalebrary:manage_locations")
    home_url_name = "whalebrary:index"
    delete_url_name = "whalebrary:delete_location"

## TAG ##


class TagHardDeleteView(WhalebraryAdminAccessRequired, CommonHardDeleteView):
    model = models.Tag
    success_url = reverse_lazy("whalebrary:manage_tags")


class TagFormsetView(WhalebraryAdminAccessRequired, CommonFormsetView):
    template_name = 'whalebrary/formset.html'
    h1 = "Manage Tags"
    queryset = models.Tag.objects.all()
    formset_class = forms.TagFormset
    success_url = reverse_lazy("whalebrary:manage_tags")
    home_url_name = "whalebrary:index"
    delete_url_name = "whalebrary:delete_tag"

## OWNER ##


class OwnerHardDeleteView(WhalebraryAdminAccessRequired, CommonHardDeleteView):
    model = models.Owner
    success_url = reverse_lazy("whalebrary:manage_owners")


class OwnerFormsetView(WhalebraryAdminAccessRequired, CommonFormsetView):
    template_name = 'whalebrary/formset.html'
    h1 = "Manage Owners"
    queryset = models.Owner.objects.all()
    formset_class = forms.OwnerFormset
    success_url = reverse_lazy("whalebrary:manage_owners")
    home_url_name = "whalebrary:index"
    delete_url_name = "whalebrary:delete_owner"

## SIZE ##


class SizeHardDeleteView(WhalebraryAdminAccessRequired, CommonHardDeleteView):
    model = models.Size
    success_url = reverse_lazy("whalebrary:manage_sizes")


class SizeFormsetView(WhalebraryAdminAccessRequired, CommonFormsetView):
    template_name = 'whalebrary/formset.html'
    h1 = "Manage Sizes"
    queryset = models.Size.objects.all()
    formset_class = forms.SizeFormset
    success_url = reverse_lazy("whalebrary:manage_sizes")
    home_url_name = "whalebrary:index"
    delete_url_name = "whalebrary:delete_size"

## ORGANISATION ##


class OrganisationHardDeleteView(WhalebraryAdminAccessRequired, CommonHardDeleteView):
    model = models.Organisation
    success_url = reverse_lazy("whalebrary:manage_organisations")


class OrganisationFormsetView(WhalebraryAdminAccessRequired, CommonFormsetView):
    template_name = 'whalebrary/formset.html'
    h1 = "Manage Organisations"
    queryset = models.Organisation.objects.all()
    formset_class = forms.OrganisationFormset
    success_url = reverse_lazy("whalebrary:manage_organisations")
    home_url_name = "whalebrary:index"
    delete_url_name = "whalebrary:delete_organisation"

## TRAINING ##


class TrainingHardDeleteView(WhalebraryAdminAccessRequired, CommonHardDeleteView):
    model = models.Training
    success_url = reverse_lazy("whalebrary:manage_trainings")


class TrainingFormsetView(WhalebraryAdminAccessRequired, CommonFormsetView):
    template_name = 'whalebrary/formset.html'
    h1 = "Manage Trainings"
    queryset = models.Training.objects.all()
    formset_class = forms.TrainingFormset
    success_url = reverse_lazy("whalebrary:manage_trainings")
    home_url_name = "whalebrary:index"
    delete_url_name = "whalebrary:delete_training"


## SPECIES ##

class SpeciesHardDeleteView(WhalebraryAdminAccessRequired, CommonHardDeleteView):
    model = models.Species
    success_url = reverse_lazy("whalebrary:manage_species")


class SpeciesFormsetView(WhalebraryAdminAccessRequired, CommonFormsetView):
    template_name = 'whalebrary/formset.html'
    h1 = "Manage Species"
    queryset = models.Species.objects.all()
    formset_class = forms.SpeciesFormset
    success_url = reverse_lazy("whalebrary:manage_species")
    home_url_name = "whalebrary:index"
    delete_url_name = "whalebrary:delete_species"

# #
# # ITEM #
# # ###########
# #
#

# TODO update this with new code that's cleaner
# TODO Decide if I want the report to also have locations
@user_passes_test(in_whalebrary_admin_group, login_url='/accounts/denied/?app=whalebrary')
def inventory_download(request):
    items = models.Item.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=inventory' + str(date.today()) + '.csv'

    writer = csv.writer(response, delimiter=',')
    writer.writerow([
        'id',
        'item_name',
        'oh quantity',
        'description',
        'note',
        'owner',
        'size',
        'category',
        'gear_type',
        'suppliers',
    ])

    for obj in items:
        writer.writerow([
            obj.id,
            obj.item_name,
            obj.total_oh_quantity,
            obj.description,
            obj.note,
            obj.owner,
            obj.size,
            obj.category,
            obj.gear_type,
            ', '.join([obj.supplier_name for obj in obj.suppliers.all()]),
        ])

    return response


class ItemListView(WhalebraryAccessRequired, CommonFilterView):
    template_name = "whalebrary/item_list.html"
    paginate_by = 50
    h1 = "Item List"
    filterset_class = filters.SpecificItemFilter
    home_url_name = "whalebrary:index"
    row_object_url_name = "whalebrary:item_detail"
    new_btn_text = "New Item"

    queryset = models.Item.objects.annotate(
        search_term=Concat('item_name', 'description', output_field=TextField()))

    field_list = [
        {"name": 'id', "class": "", "width": ""},
        {"name": 'tname|{}'.format(gettext_lazy("Item name (size)")), "class": "", "width": ""},
        {"name": 'description', "class": "", "width": ""},
        {"name": 'note', "class": "", "width": ""},
        {"name": 'owner', "class": "", "width": ""},
        {"name": 'category', "class": "red-font", "width": ""},
        {"name": 'gear_type', "class": "", "width": ""},
        {"name": 'suppliers', "class": "", "width": ""},
        {"name": 'total_oh_quantity|{}'.format(gettext_lazy("Total on hand quantity")), "class": "", "width": ""},

    ]

    def get_new_object_url(self):
        return reverse("whalebrary:item_new", kwargs=self.kwargs)


class ItemDetailView(WhalebraryAccessRequired, CommonDetailView):
    model = models.Item
    field_list = [
        'id',
        'item_name',
        'description',
        'note',
        'owner',
        'size',
        'category',
        'gear_type',
        'suppliers',
    ]
    home_url_name = "whalebrary:index"
    parent_crumb = {"title": gettext_lazy("Item List"), "url": reverse_lazy("whalebrary:item_list")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # contexts for _quantity.html file
        context["random_qty"] = models.Transaction.objects.first()
        context["oh_qty_field_list"] = [
            'location',
            'quantity',
        ]

        # context for _supplier.html
        context["random_sup"] = models.Supplier.objects.first()
        context["sup_field_list"] = [
            'supplier_name',
            'contact_number',
            'email',

        ]

        # context for _order.html
        context["random_ord"] = models.Order.objects.first()
        context["ord_field_list"] = [
            'id',
            'quantity',
            'cost',
            'date_ordered',
            'date_received',

        ]

        # context for _maintenance.html
        context["random_maint"] = models.Maintenance.objects.first()
        context["maint_field_list"] = [
            'id',
            'maint_type',
            'assigned_to',
            'last_maint_date',
            'days_until_maint|Days until maintenance required',

        ]

        # context for _lending.html
        context["random_lend"] = models.Transaction.objects.first()
        context["lend_field_list"] = [
            'quantity',
            'location',
            'comments',
        ]

        # context for _files.html
        context["random_file"] = models.File.objects.first()
        context["file_field_list"] = [
            'caption',
            'file',
            'date_uploaded',
        ]

        return context


class ItemTransactionListView(WhalebraryAdminAccessRequired, CommonFilterView):
    template_name = 'whalebrary/list.html'
    filterset_class = filters.TransactionFilter

    field_list = [
        {"name": 'item', "class": "", "width": ""},
        {"name": 'quantity', "class": "", "width": ""},
        {"name": 'category', "class": "", "width": ""},
        {"name": 'return_tracker', "class": "", "width": ""},
        {"name": 'comments', "class": "", "width": ""},
        {"name": 'audits', "class": "", "width": ""},
        {"name": 'location', "class": "", "width": ""},
        {"name": 'tags', "class": "", "width": ""},
        {"name": 'created_at', "class": "", "width": ""},
        {"name": 'created_by', "class": "", "width": ""},
        {"name": 'updated_at', "class": "", "width": ""},
    ]
    home_url_name = "whalebrary:index"
    grandparent_crumb = {"title": gettext_lazy("Item List"), "url": reverse_lazy("whalebrary:item_list")}
    row_object_url_name = "whalebrary:transaction_detail"

    def get_parent_crumb(self):
        title = models.Item.objects.get(pk=self.kwargs.get('pk'))
        return {"title": str(title), "url": reverse_lazy("whalebrary:item_detail", kwargs=self.kwargs)}

    def get_new_object_url(self):
        return reverse("whalebrary:transaction_new", kwargs=self.kwargs)

    def get_queryset(self, **kwargs):
        my_item = models.Item.objects.get(pk=self.kwargs.get('pk'))
        return my_item.transactions.all().annotate(
            search_term=Concat('id', 'item__item_name', 'quantity', 'category__type', 'comments',
                               'audits__date', 'location__location', 'tags__tag',
                               'created_at', 'created_by', 'updated_at', output_field=TextField()))

    def get_h1(self):
        item_name = models.Item.objects.get(pk=self.kwargs.get('pk'))
        h1 = _("Detailed Transactions for ") + f' {str(item_name)}'
        return h1


class ItemUpdateView(WhalebraryEditRequiredMixin, CommonUpdateView):
    model = models.Item
    form_class = forms.ItemForm
    template_name = 'whalebrary/form.html'
    cancel_text = _("Cancel")
    home_url_name = "whalebrary:index"

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Item record successfully updated for : {my_object}"))
        return HttpResponseRedirect(reverse("whalebrary:item_detail", kwargs=self.kwargs))

    def get_active_page_name_crumb(self):
        my_object = self.get_object()
        return my_object

    def get_h1(self):
        my_object = self.get_object()
        return my_object

    def get_parent_crumb(self):
        return {"title": str(self.get_object()), "url": reverse_lazy("whalebrary:item_detail", kwargs=self.kwargs)}

    def get_grandparent_crumb(self):
        kwargs = deepcopy(self.kwargs)
        del kwargs["pk"]
        return {"title": _("Item List"), "url": reverse("whalebrary:item_list", kwargs=kwargs)}


class ItemCreateView(WhalebraryEditRequiredMixin, CommonCreateView):
    model = models.Item
    form_class = forms.ItemForm
    template_name = 'whalebrary/form.html'
    home_url_name = "whalebrary:index"
    h1 = gettext_lazy("Add New Item")
    parent_crumb = {"title": gettext_lazy("Item List"), "url": reverse_lazy("whalebrary:item_list")}

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Item record successfully created for : {my_object}"))
        return super().form_valid(form)


class ItemDeleteView(WhalebraryEditRequiredMixin, CommonDeleteView):
    model = models.Item
    permission_required = "__all__"
    success_url = reverse_lazy('whalebrary:item_list')
    template_name = 'whalebrary/confirm_delete.html'
    home_url_name = "whalebrary:index"
    grandparent_crumb = {"title": gettext_lazy("Item List"), "url": reverse_lazy("whalebrary:item_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("whalebrary:item_detail", kwargs=self.kwargs)}


# # LOCATION # #

## CRUD Views - admin only

class LocationListView(WhalebraryAdminAccessRequired, CommonFilterView):
    template_name = "whalebrary/list.html"
    h1 = "Location List"
    filterset_class = filters.LocationFilter
    home_url_name = "whalebrary:index"
    row_object_url_name = "whalebrary:location_detail"
    new_btn_text = "New Location"

    queryset = models.Location.objects.annotate(
        search_term=Concat('location', 'address', output_field=TextField()))

    field_list = [
        {"name": 'id', "class": "", "width": ""},
        {"name": 'location', "class": "", "width": ""},
        {"name": 'bin_id', "class": "", "width": ""},
        {"name": 'address', "class": "", "width": ""},
        {"name": 'container', "class": "", "width": ""},
        {"name": 'container_space', "class": "", "width": ""},

    ]

    def get_new_object_url(self):
        return reverse("whalebrary:location_new", kwargs=self.kwargs)


class LocationDetailView(WhalebraryAdminAccessRequired, CommonDetailView):
    model = models.Location
    field_list = [
        'id',
        'location',
        'bin_id',
        'address',
        'container',
        'container_space',

    ]
    home_url_name = "whalebrary:index"
    parent_crumb = {"title": gettext_lazy("Location List"), "url": reverse_lazy("whalebrary:location_list")}


class LocationUpdateView(WhalebraryAdminAccessRequired, CommonUpdateView):
    model = models.Location
    form_class = forms.LocationForm
    template_name = 'whalebrary/form.html'
    cancel_text = _("Cancel")
    home_url_name = "whalebrary:index"

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Location record successfully updated for : {my_object}"))
        return HttpResponseRedirect(reverse("whalebrary:location_detail", kwargs=self.kwargs))

    def get_active_page_name_crumb(self):
        my_object = self.get_object()
        return my_object

    def get_h1(self):
        my_object = self.get_object()
        return my_object

    def get_parent_crumb(self):
        return {"title": str(self.get_object()), "url": reverse_lazy("whalebrary:location_detail", kwargs=self.kwargs)}

    def get_grandparent_crumb(self):
        kwargs = deepcopy(self.kwargs)
        del kwargs["pk"]
        return {"title": _("Location List"), "url": reverse("whalebrary:location_list", kwargs=kwargs)}


class LocationCreateView(WhalebraryAdminAccessRequired, CommonCreateView):
    model = models.Location
    form_class = forms.LocationForm
    template_name = 'whalebrary/form.html'
    home_url_name = "whalebrary:index"
    h1 = gettext_lazy("Add New Location")
    parent_crumb = {"title": gettext_lazy("Location List"), "url": reverse_lazy("whalebrary:location_list")}

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Location record successfully created for : {my_object}"))
        return super().form_valid(form)


class LocationDeleteView(WhalebraryAdminAccessRequired, CommonDeleteView):
    model = models.Location
    permission_required = "__all__"
    success_url = reverse_lazy('whalebrary:location_list')
    success_message = 'The location file was successfully deleted!'
    template_name = 'whalebrary/confirm_delete.html'
    home_url_name = "whalebrary:index"
    grandparent_crumb = {"title": gettext_lazy("Location List"), "url": reverse_lazy("whalebrary:location_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("whalebrary:location_detail", kwargs=self.kwargs)}


    ##TRANSACTION##

#TODO: Need to add verification of quantities available at locations to form_valids

def lending_return_item(request, transaction):
    """simple function to create return transaction"""
    # First get the transaction that indicates the 'lend' and toggle boolean to indicate return
    my_return = models.Transaction.objects.get(pk=transaction)
    my_return.return_tracker = True
    my_return.save()

    # Second create a new transaction that shows the return
    my_user = request.user
    my_transaction = models.Transaction.objects.create(
        item=my_return.item,
        quantity=my_return.quantity,
        category=TransactionCategory.objects.get(id=4),
        location=my_return.location,
        created_by=my_user
    )
    my_transaction.save()

    messages.success(request, "Items returned")
    return HttpResponseRedirect(reverse_lazy(
        'shared_models:close_me'))  # TODO Ideally want to have a confirm step using 'confirm_status_change.html'


# def transfer_item_to_new_location(request, item):
#     """
#     Transfer items from one location to another and create transaction records.
#     """
#     # First transaction to transfer out
#     my_item = models.Item.objects.get(pk=item)
#     my_user = request.user
#
#     out_transaction = models.Transaction.objects.create(
#         item=my_item,
#         category=TransactionCategory.objects.get(id=5),
#         created_by=my_user
#     )
#
#     return HttpResponseRedirect(
#         reverse('whalebrary:transaction_transfer', kwargs={'pk': out_transaction.id, 'pop': my_item.id}))


class TransactionTransferView(WhalebraryEditRequiredMixin, CommonCreateView):
    model = models.Transaction
    h1 = "Transfer Item From"
    submit_text = "Transfer Out"
    home_url_name = "whalebrary:index"
    parent_crumb = {"title": gettext_lazy("Transaction List"), "url": reverse_lazy("whalebrary:transaction_list")}

    def get_template_names(self):
        return "shared_models/generic_popout_form.html" if self.kwargs.get("pk") else "whalebrary/form.html"

    def get_form_class(self):
        return forms.TransactionForm1 if self.kwargs.get("pk") else forms.TransactionForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class=None)
        form.fields['location'].queryset = form.fields['location'].queryset.filter(transactions__item=self.kwargs.get("pk")).distinct()
        return form

    def form_valid(self, form):
        my_object = form.save()
        my_item = form.instance.item.id
        messages.success(self.request, _(f"Transaction record successfully created for : {my_object}"))
        success_url = reverse_lazy('whalebrary:transaction_transfer_in', kwargs={'pk': my_item})
        return HttpResponseRedirect(success_url)

    def get_initial(self):
        return {'item': self.kwargs.get('pk'),
                'category': 5,
                'created_by': self.request.user}


class TransactionTransferInView(WhalebraryEditRequiredMixin, CommonCreateView):
    model = models.Transaction
    h1 = "Transfer Item To"
    submit_text = "Transfer In"
    home_url_name = "whalebrary:index"
    parent_crumb = {"title": gettext_lazy("Transaction List"), "url": reverse_lazy("whalebrary:transaction_list")}

    def get_template_names(self):
        return "shared_models/generic_popout_form.html" if self.kwargs.get("pk") else "whalebrary/form.html"

    def get_form_class(self):
        return forms.TransactionForm1 if self.kwargs.get("pk") else forms.TransactionForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Transaction record successfully created for : {my_object}"))
        return HttpResponseRedirect(
            reverse_lazy('shared_models:close_me') if self.kwargs.get("pk") else reverse_lazy(
                'whalebrary:transaction_list'))

    def get_initial(self):
        return {'item': self.kwargs.get('pk'),
                'category': 6,
                'created_by': self.request.user}


# TODO create the location lend out function
def lend_out_item_at_location():
    """
    This should be added to _quantity.html for each line so that items can be lent
    out from a location; it should also not allow more than the # avail to be lent out
    """
    # lend_item = item.oh_quantity_by_location.get(pk=item)
    pass


# admin access only
class TransactionListView(WhalebraryAdminAccessRequired, CommonFilterView):
    template_name = "whalebrary/list.html"
    h1 = "Transaction List"
    filterset_class = filters.TransactionFilter
    home_url_name = "whalebrary:index"
    row_object_url_name = "whalebrary:transaction_detail"
    new_btn_text = "New Transaction"

    queryset = models.Transaction.objects.annotate(
        search_term=Concat('id', 'item__item_name', 'quantity', 'category__type', 'comments',
                           'audits__date', 'location__location', 'tags__tag',
                           'created_at', 'created_by', 'updated_at', output_field=TextField()))

    field_list = [
        {"name": 'item', "class": "", "width": ""},
        {"name": 'quantity', "class": "", "width": ""},
        {"name": 'category', "class": "", "width": ""},
        {"name": 'return_tracker', "class": "", "width": ""},
        {"name": 'comments', "class": "", "width": ""},
        {"name": 'audits', "class": "", "width": ""},
        {"name": 'location', "class": "", "width": ""},
        {"name": 'tags', "class": "", "width": ""},
        {"name": 'created_at', "class": "", "width": ""},
        {"name": 'created_by', "class": "", "width": ""},
        {"name": 'updated_at', "class": "", "width": ""},
    ]

    def get_new_object_url(self):
        return reverse("whalebrary:transaction_new", kwargs=self.kwargs)


class TransactionDetailView(WhalebraryAccessRequired, CommonDetailView):
    model = models.Transaction
    field_list = [
        'id',
        'item',
        'quantity',
        'category',
        'return_tracker',
        'comments',
        'audits',
        'location',
        'tags',
        'created_at',
        'created_by',
        'updated_at',

    ]
    home_url_name = "whalebrary:index"
    parent_crumb = {"title": gettext_lazy("Transaction List"), "url": reverse_lazy("whalebrary:transaction_list")}

    # def get_parent_crumb(self):
    #     parent_crumb_url = ""
    #     return {"title": self.get_object(), "url": parent_crumb_url}


class TransactionUpdateView(WhalebraryEditRequiredMixin, CommonUpdateView):
    model = models.Transaction
    form_class = forms.TransactionForm
    home_url_name = "whalebrary:index"
    template_name = "whalebrary/form.html"
    cancel_text = _("Cancel")

    def get_active_page_name_crumb(self):
        my_object = self.get_object()
        return my_object

    def get_h1(self):
        my_object = self.get_object()
        return my_object

    def get_parent_crumb(self):
        return {"title": str(self.get_object()),
                "url": reverse_lazy("whalebrary:transaction_detail", kwargs=self.kwargs)}

    def get_grandparent_crumb(self):
        return {"title": _("Transaction List"), "url": reverse("whalebrary:transaction_list")}

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Transaction record successfully updated for : {my_object}"))
        return HttpResponseRedirect(reverse("whalebrary:transaction_detail", kwargs=self.kwargs))

    def get_initial(self):
        return {'created_by': self.request.user}


# TODO change this to a lending by location popout view/form
# class TransactionUpdatePopoutView(WhalebraryEditRequiredMixin, CommonPopoutUpdateView):
#     model = models.Transaction
#     form_class = forms.TransactionForm1

class TransactionAddCreateView(WhalebraryEditRequiredMixin, CommonCreateView):
    model = models.Transaction
    home_url_name = "whalebrary:index"
    parent_crumb = {"title": gettext_lazy("Transaction List"), "url": reverse_lazy("whalebrary:transaction_list")}

    def get_template_names(self):
        return "shared_models/generic_popout_form.html" if self.kwargs.get("pk") else "whalebrary/form.html"

    def get_form_class(self):
        return forms.TransactionForm1 if self.kwargs.get("pk") else forms.TransactionForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Transaction record successfully created for : {my_object}"))
        return HttpResponseRedirect(
            reverse_lazy('shared_models:close_me') if self.kwargs.get("pk") else reverse_lazy(
                'whalebrary:transaction_list'))

    def get_initial(self):
        return {'item': self.kwargs.get('pk'),
                'category': 1,
                'created_by': self.request.user}


class TransactionUseCreateView(WhalebraryEditRequiredMixin, CommonCreateView):
    model = models.Transaction
    home_url_name = "whalebrary:index"
    parent_crumb = {"title": gettext_lazy("Transaction List"), "url": reverse_lazy("whalebrary:transaction_list")}

    def get_template_names(self):
        return "shared_models/generic_popout_form.html" if self.kwargs.get("pk") else "whalebrary/form.html"

    def get_form_class(self):
        return forms.TransactionForm1 if self.kwargs.get("pk") else forms.TransactionForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class=None)
        form.fields['location'].queryset = form.fields['location'].queryset.filter(transactions__item=self.kwargs.get("pk")).distinct()
        return form

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Transaction record successfully created for : {my_object}"))
        return HttpResponseRedirect(
            reverse_lazy('shared_models:close_me') if self.kwargs.get("pk") else reverse_lazy(
                'whalebrary:transaction_list'))

    def get_initial(self):
        return {'item': self.kwargs.get('pk'),
                'category': 2,
                'created_by': self.request.user}


class TransactionLendCreateView(WhalebraryEditRequiredMixin, CommonCreateView):
    model = models.Transaction
    form_class = forms.TransactionForm2
    template_name = 'shared_models/generic_popout_form.html'
    home_url_name = "whalebrary:index"
    submit_text = "Borrow"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=None)
        form.fields['location'].queryset = form.fields['location'].queryset.filter(transactions__item=self.kwargs.get("pk")).distinct()
        return form

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Transaction record successfully created for : {my_object}"))
        return HttpResponseRedirect(reverse_lazy('shared_models:close_me'))

    def get_initial(self):
        return {'item': self.kwargs.get('pk'),
                'category': TransactionCategory.objects.get(id=3),
                'created_by': self.request.user
                }


# class TransactionTransferCreateView(WhalebraryEditRequiredMixin, CommonCreateView):
#     model = models.Transaction
#     form_class = forms.TransactionForm2
#     template_name = 'shared_models/generic_popout_form.html'
#     home_url_name = "whalebrary:index"
#     submit_text = "Transfer"
#
#     def form_valid(self, form):
#         my_object = form.save()
#         messages.success(self.request, _(f"Transaction record successfully created for : {my_object}"))
#         return HttpResponseRedirect(reverse_lazy('shared_models:close_me'))
#
#     def get_initial(self):
#         return {'item': self.kwargs.get('pk'),
#                 'category': TransactionCategory.objects.get(id=5),
#                 'created_by': self.request.user
#                 }


class TransactionDeleteView(WhalebraryEditRequiredMixin, CommonDeleteView):
    model = models.Transaction
    permission_required = "__all__"
    success_url = reverse_lazy('whalebrary:transaction_list')
    template_name = 'whalebrary/confirm_delete.html'
    home_url_name = "whalebrary:index"
    grandparent_crumb = {"title": gettext_lazy("Transaction List"), "url": reverse_lazy("whalebrary:transaction_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("whalebrary:transaction_detail", kwargs=self.kwargs)}


class TransactionDeletePopoutView(WhalebraryEditRequiredMixin, CommonPopoutDeleteView):
    model = models.Transaction
    delete_protection = False


    ## LENDING ##


class LendingListView(WhalebraryAccessRequired, CommonFilterView):
    template_name = "whalebrary/lending_list.html"
    h1 = "Lending List"
    filterset_class = filters.LendingFilter
    home_url_name = "whalebrary:index"
    row_object_url_name = "whalebrary:item_detail"
    # new_btn_text = "New Lending Record"

    queryset = models.Transaction.objects.annotate(
        search_term=Concat('id', 'item__item_name', 'quantity', 'category__type', 'comments',
                           'location__location', 'created_by__first_name',
                           output_field=TextField())).filter(category=3, return_tracker=False)

    field_list = [
        {"name": 'id', "class": "", "width": ""},
        {"name": 'item', "class": "", "width": ""},
        {"name": 'quantity', "class": "", "width": ""},
        {"name": 'category', "class": "", "width": ""},
        {"name": 'comments', "class": "", "width": ""},
        {"name": 'location', "class": "", "width": ""},
        {"name": 'created_at', "class": "", "width": ""},
        {"name": 'created_by', "class": "", "width": ""},
        {"name": 'updated_at', "class": "", "width": ""},

    ]

    # def get_new_object_url(self):
    #     return reverse("whalebrary:maintenance_new", kwargs=self.kwargs)


    ##BULK TRANSACTION##


class BulkTransactionListView(WhalebraryAdminAccessRequired, CommonFilterView):
    template_name = 'whalebrary/bulk_transaction_list.html'
    filterset_class = filters.BulkTransactionFilter
    h1 = "Item Quantities and Statuses"
    home_url_name = "whalebrary:index"
    row_object_url_name = "whalebrary:transaction_detail"

    queryset = models.Transaction.objects.annotate(
        search_term=Concat('id', 'item__item_name', 'quantity', 'category__type', 'location__location',
                           output_field=TextField()))

    field_list = [
        {"name": 'id', "class": "", "width": ""},
        {"name": 'item', "class": "", "width": "100px"},
        {"name": 'quantity', "class": "", "width": ""},
        {"name": 'category', "class": "", "width": "75px"},
        {"name": 'location', "class": "", "width": ""},

    ]


# from https://github.com/ccnmtl/dmt/blob/master/dmt/main/views.py#L614
# class BulkTransactionDetailView(WhalebraryAdminAccessRequired, DetailView):
#     model = models.Transaction #or should this be Transaction? TBD
#
#     @staticmethod
#     def reassign_status(request, transactions, new_status):
#         item_names = []
#         for pk in transactions:
#             item = get_object_or_404(models.Transaction, pk=pk)
#             item.reassign(request.transaction.status, new_status, '')
#             item_names.append(
#                 '<a href="{}">{}</a>'.format(
#                     item.get_absolute_url(), item.item_name))
#
#         if len(item_names) > 0:
#             msg = 'Assigned the following items to ' + \
#                   '<strong>{}</strong>: {}'.format(
#                       new_status.get_fullname(),
#                       ', '.join(item_names))
#             messages.success(request, mark_safe(msg))
#
#     def post(self, request, *args, **kwargs):
#         action = request.POST.get('action')
#         transactions = request.POST.getlist('_selected_action')
#
#         if action == 'edit' and request.POST.get('edit_status'):
#             edit_status = request.POST.get('edit_status')
#             status = get_object_or_404(Status, name=edit_status)
#             self.reassign_status(request, transactions, status)
#
#         return HttpResponseRedirect(
#             reverse('bulk_transaction_detail', args=args, kwargs=kwargs))


class BulkTransactionDeleteView(WhalebraryAdminAccessRequired, CommonDeleteView):
    model = models.Transaction
    permission_required = "__all__"
    success_url = reverse_lazy('whalebrary:bulk_transaction_list')
    # success_message = 'The transaction was successfully deleted!' # TODO doesn't currently work
    template_name = 'whalebrary/confirm_delete.html'
    home_url_name = "whalebrary:index"
    parent_crumb = {"title": gettext_lazy("Item Quantities and Statuses"),
                    "url": reverse_lazy("whalebrary:bulk_transaction_list")}


# TODO write a view for this
class ConfirmStatusChangeView(WhalebraryAdminAccessRequired, CommonPopoutFormView):
    pass

    ## ORDER ##


class OrderListView(WhalebraryAccessRequired, CommonFilterView):
    template_name = "whalebrary/order_list.html"
    h1 = "Order List"
    paginate_by = 50
    filterset_class = filters.OrderFilter
    home_url_name = "whalebrary:index"
    row_object_url_name = "whalebrary:order_detail"
    new_btn_text = "New Order"

    queryset = models.Order.objects.annotate(
        search_term=Concat('id', 'item__item_name', 'quantity', 'cost', 'date_ordered', 'date_received',
                           'transaction__id',
                           output_field=TextField()))

    field_list = [
        {"name": 'id', "class": "", "width": ""},
        {"name": 'item', "class": "", "width": ""},
        {"name": 'quantity', "class": "", "width": ""},
        {"name": 'cost', "class": "", "width": ""},
        {"name": 'date_ordered', "class": "", "width": ""},
        {"name": 'date_received', "class": "", "width": ""},
        {"name": 'trans_id|Transaction id', "class": "", "width": ""},

    ]

    def get_new_object_url(self):
        return reverse("whalebrary:order_new", kwargs=self.kwargs)


class OrderDetailView(WhalebraryAccessRequired, CommonDetailView):
    model = models.Order
    field_list = [
        'id',
        'item',
        'quantity',
        'cost',
        'date_ordered',
        'date_received',
        'trans_id|Transaction id',

    ]
    home_url_name = "whalebrary:index"

    def get_h1(self):
        order_num = models.Order.objects.get(pk=self.kwargs.get('pk'))
        h1 = _("Order # ") + f' {str(order_num)}'
        return h1

    def get_parent_crumb(self):
        return {"title": gettext_lazy("Order List"), "url": reverse_lazy("whalebrary:order_list")}

    # def get_parent_crumb(self):
    #     parent_crumb_url = ""
    #     return {"title": self.get_object(), "url": parent_crumb_url}


class OrderUpdateView(WhalebraryEditRequiredMixin, CommonUpdateView):
    model = models.Order
    form_class = forms.OrderForm
    home_url_name = "whalebrary:index"
    template_name = "whalebrary/form.html"
    cancel_text = _("Cancel")

    def get_h1(self):
        order_num = models.Order.objects.get(pk=self.kwargs.get('pk'))
        h1 = _("Order # ") + f' {str(order_num)}'
        return h1

    def get_parent_crumb(self):
        return {"title": str(self.get_h1()),
                "url": reverse_lazy("whalebrary:order_detail", kwargs=self.kwargs)}

    def get_grandparent_crumb(self):
        return {"title": _("Order List"), "url": reverse("whalebrary:order_list")}

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Order record successfully updated for : {my_object}"))
        return HttpResponseRedirect(reverse("whalebrary:order_detail", kwargs=self.kwargs))


class OrderUpdatePopoutView(WhalebraryEditRequiredMixin, CommonPopoutUpdateView):
    model = models.Order
    form_class = forms.OrderForm1


# TODO Figure out how to have it only create once the form is saved - confirmation html step?

def mark_order_received(request, order):
    """function to mark order received and create new transaction"""
    # put in check to see if user wants to do this, javascript
    # XYZ

    # record received date
    my_order = models.Order.objects.get(pk=order)
    my_order.date_received = timezone.now()
    my_order.save()
    messages.success(request, "Order received")

    # create new purchase transaction for received items
    my_user = request.user
    my_transaction = models.Transaction.objects.create(
        item=my_order.item,
        quantity=my_order.quantity,
        category=TransactionCategory.objects.get(id=1),
        location=Location.objects.get(location='Temp'),
        created_by=my_user
    )
    # my_transaction.tag.add(3)
    my_order.transaction = my_transaction
    my_order.save()

    return HttpResponseRedirect(
        reverse('whalebrary:transaction_edit', kwargs={'pk': my_transaction.id, 'pop': my_order.id}))


class OrderReceivedTransactionUpdateView(WhalebraryEditRequiredMixin, CommonPopoutUpdateView):
    model = models.Transaction
    form_class = forms.TransactionForm2


class OrderCreateView(WhalebraryEditRequiredMixin, CommonCreateView):
    model = models.Order
    home_url_name = "whalebrary:index"
    parent_crumb = {"title": gettext_lazy("Order List"), "url": reverse_lazy("whalebrary:order_list")}

    def get_template_names(self):
        return "shared_models/generic_popout_form.html" if self.kwargs.get("pk") else "whalebrary/form.html"

    def get_form_class(self):
        return forms.OrderForm1 if self.kwargs.get("pk") else forms.OrderForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Order record successfully created for : Order # {str(my_object)}"))

        # if there's a pk argument, this means user is calling from item_detail page and
        if self.kwargs.get("pk"):
            my_item = models.Item.objects.get(pk=self.kwargs.get("pk"))
            my_item.orders.add(my_object)
            return HttpResponseRedirect(reverse_lazy('shared_models:close_me'))
        else:
            return HttpResponseRedirect(reverse_lazy('whalebrary:order_list'))

    def get_initial(self):
        return {'item': self.kwargs.get('pk')}


class OrderDeleteView(WhalebraryEditRequiredMixin, CommonDeleteView):
    model = models.Order
    permission_required = "__all__"
    success_url = reverse_lazy('whalebrary:order_list')
    template_name = 'whalebrary/confirm_delete.html'
    home_url_name = "whalebrary:index"
    grandparent_crumb = {"title": gettext_lazy("Order List"), "url": reverse_lazy("whalebrary:order_list")}

    def get_parent_crumb(self):
        return {"title": "Order # " + str(self.get_object()),
                "url": reverse_lazy("whalebrary:order_detail", kwargs=self.kwargs)}


class OrderDeletePopoutView(WhalebraryEditRequiredMixin, CommonPopoutDeleteView):
    model = models.Order
    delete_protection = False

    ## MAINTENANCE ##


class MaintenanceListView(WhalebraryAccessRequired, CommonFilterView):
    template_name = "whalebrary/maintenance_list.html"
    h1 = "Maintenance List"
    filterset_class = filters.MaintenanceFilter
    home_url_name = "whalebrary:index"
    row_object_url_name = "whalebrary:maintenance_detail"
    new_btn_text = "New Maintenance Record"

    queryset = models.Maintenance.objects.annotate(
        search_term=Concat('id', 'item__item_name', 'maint_type', 'schedule', 'assigned_to', 'comments',
                           'last_maint_by', 'last_maint_date',
                           output_field=TextField()))

    field_list = [
        {"name": 'id', "class": "", "width": ""},
        {"name": 'item', "class": "", "width": ""},
        {"name": 'maint_type', "class": "", "width": ""},
        {"name": 'schedule', "class": "", "width": ""},
        {"name": 'assigned_to', "class": "", "width": ""},
        {"name": 'comments', "class": "", "width": ""},
        {"name": 'last_maint_by', "class": "", "width": ""},
        {"name": 'last_maint_date', "class": "", "width": ""},
        {"name": 'days_until_maint|Days until maintenance required', "class": "red-font", "width": ""},

    ]

    def get_new_object_url(self):
        return reverse("whalebrary:maintenance_new", kwargs=self.kwargs)


class MaintenanceDetailView(WhalebraryAccessRequired, CommonDetailView):
    model = models.Maintenance
    field_list = [
        'id',
        'item',
        'maint_type',
        'schedule',
        'assigned_to',
        'comments',
        'last_maint_by',
        'last_maint_date',

    ]
    home_url_name = "whalebrary:index"

    # def get_h1(self):
    #     order_num = models.Order.objects.get(pk=self.kwargs.get('pk'))
    #     h1 = _("Order # ") + f' {str(order_num)}'
    #     return h1

    def get_parent_crumb(self):
        return {"title": gettext_lazy("Maintenance List"), "url": reverse_lazy("whalebrary:maintenance_list")}

    # def get_parent_crumb(self):
    #     parent_crumb_url = ""
    #     return {"title": self.get_object(), "url": parent_crumb_url}


class MaintenanceUpdateView(WhalebraryEditRequiredMixin, CommonUpdateView):
    model = models.Maintenance
    form_class = forms.MaintenanceForm
    home_url_name = "whalebrary:index"
    template_name = "whalebrary/form.html"
    cancel_text = _("Cancel")

    # def get_h1(self):
    #     order_num = models.Maintenance.objects.get(pk=self.kwargs.get('pk'))
    #     h1 = _("Order # ") + f' {str(order_num)}'
    #     return h1

    def get_parent_crumb(self):
        return {"title": str(self.get_h1()),
                "url": reverse_lazy("whalebrary:maintenance_detail", kwargs=self.kwargs)}

    def get_grandparent_crumb(self):
        return {"title": _("Maintenance List"), "url": reverse("whalebrary:maintenance_list")}

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Maintenance record successfully updated for : {my_object}"))
        return HttpResponseRedirect(reverse("whalebrary:maintenance_detail", kwargs=self.kwargs))


class MaintenanceUpdatePopoutView(WhalebraryEditRequiredMixin, CommonPopoutUpdateView):
    model = models.Maintenance
    form_class = forms.MaintenanceForm1


def mark_maintenance_done(request, maintenance):
    """function to log that a new maintenance has been completed"""
    # put in check to see if user wants to do this, javascript
    # XYZ

    # record logged in user and today's date
    my_maintenance = models.Maintenance.objects.get(pk=maintenance)
    my_user = request.user
    my_maintenance.last_maint_date = timezone.now()
    my_maintenance.last_maint_by = my_user
    my_maintenance.save()
    messages.success(request, "New maintenance completed!")

    return HttpResponseRedirect(reverse_lazy('shared_models:close_me'))

#
# class OrderReceivedTransactionUpdateView(WhalebraryEditRequiredMixin, CommonPopoutUpdateView):
#     model = models.Transaction
#     form_class = forms.TransactionForm2


class MaintenanceCreateView(WhalebraryEditRequiredMixin, CommonCreateView):
    model = models.Maintenance
    home_url_name = "whalebrary:index"
    parent_crumb = {"title": gettext_lazy("Maintenance List"), "url": reverse_lazy("whalebrary:maintenance_list")}

    def get_template_names(self):
        return "shared_models/generic_popout_form.html" if self.kwargs.get("pk") else "whalebrary/form.html"

    def get_form_class(self):
        return forms.MaintenanceForm1 if self.kwargs.get("pk") else forms.MaintenanceForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class=None)
        form.fields['assigned_to'].queryset = form.fields['assigned_to'].queryset.filter(groups__name__in=["whalebrary_admin", "whalebrary_edit"])
        return form

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Maintenance record successfully created for : Item # {str(my_object)}"))

        # if there's a pk argument, this means user is calling from item_detail page and
        if self.kwargs.get("pk"):
            my_item = models.Item.objects.get(pk=self.kwargs.get("pk"))
            my_item.maintenances.add(my_object)
            return HttpResponseRedirect(reverse_lazy('shared_models:close_me'))
        else:
            return HttpResponseRedirect(reverse_lazy('whalebrary:maintenance_list'))

    def get_initial(self):
        return {'item': self.kwargs.get('pk')}


class MaintenanceDeleteView(WhalebraryEditRequiredMixin, CommonDeleteView):
    model = models.Maintenance
    permission_required = "__all__"
    success_url = reverse_lazy('whalebrary:maintenance_list')
    template_name = 'whalebrary/confirm_delete.html'
    home_url_name = "whalebrary:index"
    grandparent_crumb = {"title": gettext_lazy("Maintenance List"), "url": reverse_lazy("whalebrary:maintenance_list")}

    def get_parent_crumb(self):
        return {"title": str(self.get_object()),
                "url": reverse_lazy("whalebrary:maintenance_detail", kwargs=self.kwargs)}


class MaintenanceDeletePopoutView(WhalebraryEditRequiredMixin, CommonPopoutDeleteView):
    model = models.Maintenance
    delete_protection = False


    ## PERSONNEL ##


class PersonnelListView(WhalebraryAdminAccessRequired, CommonFilterView):
    template_name = "whalebrary/personnel_list.html"
    h1 = "Personnel List"
    filterset_class = filters.PersonnelFilter
    home_url_name = "whalebrary:index"
    row_object_url_name = "whalebrary:personnel_detail"
    new_btn_text = "New Personnel"

    queryset = models.Personnel.objects.annotate(
        search_term=Concat('id', 'first_name', 'last_name', 'organisation__name', 'email', 'phone',
                           'exp_level__name', output_field=TextField()))

    field_list = [
        {"name": 'id', "class": "", "width": ""},
        {"name": 'first_name', "class": "", "width": ""},
        {"name": 'last_name', "class": "", "width": ""},
        {"name": 'organisation', "class": "", "width": ""},
        {"name": 'email', "class": "", "width": ""},
        {"name": 'exp_level', "class": "", "width": ""},
        {"name": 'trainings', "class": "", "width": ""},
    ]

    def get_new_object_url(self):
        return reverse("whalebrary:personnel_new", kwargs=self.kwargs)


class PersonnelDetailView(WhalebraryAdminAccessRequired, CommonDetailView):
    model = models.Personnel
    field_list = [
        'id',
        'first_name',
        'last_name',
        'organisation',
        'email',
        'phone',
        'exp_level',
        'trainings',

    ]
    home_url_name = "whalebrary:index"
    parent_crumb = {"title": gettext_lazy("Personnel List"), "url": reverse_lazy("whalebrary:personnel_list")}


class PersonnelUpdateView(WhalebraryAdminAccessRequired, CommonUpdateView):
    model = models.Personnel
    form_class = forms.PersonnelForm
    template_name = 'whalebrary/form.html'
    cancel_text = _("Cancel")
    home_url_name = "whalebrary:index"

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Personnel record successfully updated for : {my_object}"))
        return HttpResponseRedirect(reverse("whalebrary:personnel_detail", kwargs=self.kwargs))

    def get_active_page_name_crumb(self):
        my_object = self.get_object()
        return my_object

    def get_h1(self):
        my_object = self.get_object()
        return my_object

    def get_parent_crumb(self):
        return {"title": str(self.get_object()), "url": reverse_lazy("whalebrary:personnel_detail", kwargs=self.kwargs)}

    def get_grandparent_crumb(self):
        kwargs = deepcopy(self.kwargs)
        del kwargs["pk"]
        return {"title": _("Personnel List"), "url": reverse("whalebrary:personnel_list", kwargs=kwargs)}


class PersonnelCreateView(WhalebraryAdminAccessRequired, CommonCreateView):
    model = models.Personnel
    form_class = forms.PersonnelForm
    template_name = 'whalebrary/form.html'
    home_url_name = "whalebrary:index"
    h1 = gettext_lazy("Add New Personnel")
    parent_crumb = {"title": gettext_lazy("Personnel List"), "url": reverse_lazy("whalebrary:personnel_list")}

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Personnel record successfully created for : {my_object}"))
        return super().form_valid(form)


class PersonnelDeleteView(WhalebraryAdminAccessRequired, CommonDeleteView):
    model = models.Personnel
    permission_required = "__all__"
    success_url = reverse_lazy('whalebrary:personnel_list')
    success_message = 'The personnel file was successfully deleted!'
    template_name = 'whalebrary/confirm_delete.html'
    home_url_name = "whalebrary:index"
    grandparent_crumb = {"title": gettext_lazy("Personnel List"), "url": reverse_lazy("whalebrary:personnel_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("whalebrary:personnel_detail", kwargs=self.kwargs)}

    ## SUPPLIER ##


def add_supplier_to_item(request, supplier, item):
    """simple function to add supplier to item"""
    my_item = models.Item.objects.get(pk=item)
    my_supplier = models.Supplier.objects.get(pk=supplier)
    my_item.suppliers.add(my_supplier)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


class AddSuppliersToItemView(WhalebraryEditRequiredMixin, CommonPopoutFormView):
    h1 = gettext_lazy("Please select a supplier to add to item")
    form_class = forms.IncidentForm  # TODO just a temp placeholder until we create a CommonPopoutTemplateView
    template_name = "whalebrary/supplier_list_popout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["suppliers"] = models.Supplier.objects.all()
        return context


def remove_supplier_from_item(request, supplier, item):
    """simple function to remove supplier from item"""
    my_item = models.Item.objects.get(pk=item)
    my_supplier = models.Supplier.objects.get(pk=supplier)
    my_item.suppliers.remove(my_supplier)
    return HttpResponseRedirect(reverse_lazy('shared_models:close_me'))


class SupplierListView(WhalebraryAccessRequired, CommonFilterView):
    template_name = "whalebrary/list.html"
    h1 = "Supplier List"
    filterset_class = filters.SupplierFilter
    home_url_name = "whalebrary:index"
    row_object_url_name = "whalebrary:supplier_detail"
    new_btn_text = "New Supplier"

    queryset = models.Supplier.objects.annotate(
        search_term=Concat('id', 'supplier_name', 'contact_number', 'email', 'website', 'comments',
                           output_field=TextField()))

    field_list = [
        {"name": 'id', "class": "", "width": ""},
        {"name": 'supplier_name', "class": "", "width": ""},
        {"name": 'contact_number', "class": "", "width": ""},
        {"name": 'comments', "class": "", "width": ""},

    ]

    def get_new_object_url(self):
        return reverse("whalebrary:supplier_new", kwargs=self.kwargs)


class SupplierDetailView(WhalebraryAccessRequired, CommonDetailView):
    model = models.Supplier

    field_list = [
        'id',
        'supplier_name',
        'contact_number',
        'email',
        'website',
        'comments',

    ]

    home_url_name = "whalebrary:index"

    def get_parent_crumb(self):
        return {"title": _("Supplier List"), "url": reverse("whalebrary:supplier_list")}


class SupplierUpdateView(WhalebraryEditRequiredMixin, CommonUpdateView):
    model = models.Supplier
    form_class = forms.SupplierForm
    home_url_name = "whalebrary:index"
    template_name = "whalebrary/form.html"
    cancel_text = _("Cancel")

    def get_active_page_name_crumb(self):
        my_object = self.get_object()
        return my_object

    def get_h1(self):
        my_object = self.get_object()
        return my_object

    def get_parent_crumb(self):
        return {"title": str(self.get_object()),
                "url": reverse_lazy("whalebrary:supplier_detail", kwargs=self.kwargs)}

    def get_grandparent_crumb(self):
        return {"title": _("Supplier List"), "url": reverse("whalebrary:supplier_list")}

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Supplier record successfully updated for : {my_object}"))
        return HttpResponseRedirect(reverse("whalebrary:supplier_detail", kwargs=self.kwargs))


class SupplierUpdatePopoutView(WhalebraryEditRequiredMixin, CommonPopoutUpdateView):
    model = models.Supplier
    form_class = forms.SupplierForm1


class SupplierCreateView(WhalebraryEditRequiredMixin, CommonCreateView):
    model = models.Supplier
    home_url_name = "whalebrary:index"
    parent_crumb = {"title": gettext_lazy("Supplier List"), "url": reverse_lazy("whalebrary:supplier_list")}

    def get_template_names(self):
        return "shared_models/generic_popout_form.html" if self.kwargs.get("pk") else "whalebrary/form.html"

    def get_form_class(self):
        return forms.SupplierForm1 if self.kwargs.get("pk") else forms.SupplierForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Supplier record successfully created for : {my_object}"))

        # if there's a pk argument, this means user is calling from item_detail page and
        if self.kwargs.get("pk"):
            my_item = models.Item.objects.get(pk=self.kwargs.get("pk"))
            my_item.suppliers.add(my_object)
            return HttpResponseRedirect(reverse_lazy('shared_models:close_me'))
        else:
            return HttpResponseRedirect(reverse_lazy('whalebrary:supplier_list'))

    def get_initial(self):
        return {'item': self.kwargs.get('pk')}


class SupplierDeleteView(WhalebraryEditRequiredMixin, CommonDeleteView):
    model = models.Supplier
    permission_required = "__all__"
    success_url = reverse_lazy('whalebrary:supplier_list')
    template_name = 'whalebrary/confirm_delete.html'
    home_url_name = "whalebrary:index"
    grandparent_crumb = {"title": gettext_lazy("Supplier List"), "url": reverse_lazy("whalebrary:supplier_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("whalebrary:supplier_detail", kwargs=self.kwargs)}


class SupplierDeletePopoutView(WhalebraryEditRequiredMixin, CommonPopoutDeleteView):
    model = models.Supplier
    delete_protection = False

    ## ITEM FILE UPLOAD ##


class FileListView(WhalebraryAdminAccessRequired, CommonFilterView):
    template_name = "whalebrary/file_list.html"
    h1 = "File List"
    filterset_class = filters.FileFilter
    home_url_name = "whalebrary:index"
    # new_btn_text = "New File"

    queryset = models.File.objects.annotate(
        search_term=Concat('id', 'item__item_name', 'caption', 'file', 'date_uploaded', output_field=TextField()))

    field_list = [
        {"name": 'id', "class": "", "width": ""},
        {"name": 'item', "class": "", "width": "100px"},
        {"name": 'caption', "class": "", "width": ""},
        {"name": 'file', "class": "", "width": "75px"},
        {"name": 'date_uploaded', "class": "", "width": "100px"},

    ]

    # def get_new_object_url(self):
    #     return reverse("whalebrary:file_new", kwargs=self.kwargs)


class FileCreateView(WhalebraryEditRequiredMixin, CommonCreateView):
    model = models.File
    template_name = 'whalebrary/file_form_popout.html'
    form_class = forms.FileForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"File successfully added for : {my_object}"))
        return HttpResponseRedirect(reverse_lazy('shared_models:close_me'))

    def get_initial(self):
        item = models.Item.objects.get(pk=self.kwargs['item'])
        return {
            'item': item,
        }


class FileUpdateView(WhalebraryEditRequiredMixin, CommonUpdateView):
    model = models.File
    template_name = 'whalebrary/file_form_popout.html'
    form_class = forms.FileForm
    cancel_text = _("Cancel")

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"File record successfully updated for : {my_object}"))
        success_url = reverse_lazy('shared_models:close_me')
        return HttpResponseRedirect(success_url)


# This view is not currently being used
#
# class FileDetailView(FileUpdateView):
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["editable"] = False
#         return context


class FileDeleteView(WhalebraryEditRequiredMixin, CommonPopoutDeleteView):
    model = models.File
    delete_protection = False

    ## INCIDENT ##


class IncidentListView(WhalebraryAccessRequired, CommonFilterView):
    template_name = "whalebrary/incident_list.html"
    h1 = "Incident List"
    filterset_class = filters.IncidentFilter
    home_url_name = "whalebrary:index"
    row_object_url_name = "whalebrary:incident_detail"
    new_btn_text = "New Incident"

    queryset = models.Incident.objects.annotate(
        search_term=Concat('id', 'name', 'location', 'region', 'species__name',
                           output_field=TextField()))

    field_list = [
        {"name": 'id', "class": "", "width": ""},
        {"name": 'incident_id|{}'.format(gettext_lazy("Incident ID")), "class": "", "width": "100px"},
        {"name": 'name', "class": "", "width": ""},
        {"name": 'species_count', "class": "", "width": ""},
        {"name": 'submitted', "class": "", "width": ""},
        {"name": 'first_report', "class": "", "width": ""},
        {"name": 'location', "class": "", "width": ""},
        {"name": 'region', "class": "", "width": ""},
        {"name": 'species', "class": "", "width": ""},
        {"name": 'incident_type', "class": "", "width": ""},
        {"name": 'response', "class": "", "width": ""},
        {"name": 'date_email_sent', "class": "", "width": ""},
    ]

    def get_new_object_url(self):
        return reverse("whalebrary:incident_new", kwargs=self.kwargs)


class IncidentDetailView(WhalebraryAccessRequired, CommonDetailView):
    model = models.Incident
    field_list = [
        'id',
        'incident_id|{}'.format(gettext_lazy("Incident ID")),
        'name',
        'species_count',
        'submitted',
        'reported_by',
        'first_report',
        'coordinates',
        'location',
        'region',
        'species',
        'sex',
        'age_group',
        'incident_type',
        'gear_presence',
        'gear_desc',
        'response',
        'response_type',
        'response_by',
        'response_date',
        'necropsy',
        'results',
        'photos',
        # 'data_folder',
        'data_folder_path|{}'.format(gettext_lazy(r"Data folder (Y:\path\folder)")),
        'comments',
        'date_email_sent',

    ]
    home_url_name = "whalebrary:index"
    parent_crumb = {"title": gettext_lazy("Incident List"), "url": reverse_lazy("whalebrary:incident_list")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # context for _image.html
        context["random_image"] = models.Image.objects.first()
        context["image_field_list"] = [
            'title',
            'date_uploaded',
        ]

        # context for _resight.html
        context["random_resight"] = models.Resight.objects.first()
        context["resight_field_list"] = [
            'id',
            'coordinates',
            'reported_by',
            'resight_date',
            'comments',
            'date_email_sent',
        ]


        # contexts for incident_detail maps
        context["all_incidents"] = [i.get_leaflet_dict() for i in models.Incident.objects.filter(latitude__isnull=False, longitude__isnull=False)]
        context["obj_resights"] = [i.get_leaflet_resight_dict() for i in models.Resight.objects.filter(latitude__isnull=False, longitude__isnull=False, incident__id__iexact=self.kwargs['pk'])]
        context["mapbox_api_key"] = settings.MAPBOX_API_KEY

        return context


def send_incident_email(request, pk):
    """simple function to send email with detail_view information"""
    # create a new email object
    incident = get_object_or_404(models.Incident, pk=pk)
    email = emails.NewIncidentEmail(request, incident)
    # send the email object
    email.send()
    # success message
    messages.success(request, "The new incident has been logged and a confirmation email has been sent!")
    # log when the email was sent
    incident.date_email_sent = timezone.now()
    incident.save()
    # go to previous page
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


class IncidentUpdateView(WhalebraryEditRequiredMixin, CommonUpdateView):
    model = models.Incident
    form_class = forms.IncidentForm
    template_name = 'whalebrary/form.html'
    cancel_text = _("Cancel")
    home_url_name = "whalebrary:index"

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Incident record successfully updated for : {my_object}"))
        return HttpResponseRedirect(reverse("whalebrary:incident_detail", kwargs=self.kwargs))

    def get_active_page_name_crumb(self):
        my_object = self.get_object()
        return my_object

    def get_h1(self):
        my_object = self.get_object()
        return my_object

    def get_parent_crumb(self):
        return {"title": str(self.get_object()), "url": reverse_lazy("whalebrary:incident_detail", kwargs=self.kwargs)}

    def get_grandparent_crumb(self):
        kwargs = deepcopy(self.kwargs)
        del kwargs["pk"]
        return {"title": _("Incident List"), "url": reverse("whalebrary:incident_list", kwargs=kwargs)}


class IncidentCreateView(WhalebraryEditRequiredMixin, CommonCreateView):
    model = models.Incident
    form_class = forms.IncidentForm
    template_name = 'whalebrary/form.html'
    home_url_name = "whalebrary:index"
    h1 = gettext_lazy("Add New Incident")
    parent_crumb = {"title": gettext_lazy("Incident List"), "url": reverse_lazy("whalebrary:incident_list")}

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Incident record successfully created for : {my_object}"))
        return super().form_valid(form)


class IncidentDeleteView(WhalebraryEditRequiredMixin, CommonDeleteView):
    model = models.Incident
    permission_required = "__all__"
    success_url = reverse_lazy('whalebrary:incident_list')
    success_message = 'The incident file was successfully deleted!'
    template_name = 'whalebrary/confirm_delete.html'
    home_url_name = "whalebrary:index"
    grandparent_crumb = {"title": gettext_lazy("Incident List"), "url": reverse_lazy("whalebrary:incident_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("whalebrary:incident_detail", kwargs=self.kwargs)}

        ## INCIDENT RESIGHT ##


def send_resight_email(request, pk):
    """simple function to send email with detail_view information"""
    # create a new email object
    resight = get_object_or_404(models.Resight, pk=pk)
    email = emails.NewResightEmail(request, resight)
    # send the email object
    email.send()
    # success message
    messages.success(request, "The new incident has been logged and a confirmation email has been sent!")
    # log when the email was sent
    resight.date_email_sent = timezone.now()
    resight.save()
    # go to previous page
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


class ResightListView(WhalebraryAccessRequired, CommonFilterView):
    template_name = "whalebrary/list.html"
    h1 = "Resight List"
    filterset_class = filters.ResightFilter
    home_url_name = "whalebrary:index"
    row_object_url_name = "whalebrary:resight_detail"
    # new_btn_text = "New Resight"

    queryset = models.Resight.objects.annotate(
        search_term=Concat('id', 'reported_by', 'comments',
                           output_field=TextField()))

    field_list = [
        {"name": 'id', "class": "", "width": ""},
        {"name": 'reported_by', "class": "", "width": ""},
        {"name": 'resight_date', "class": "", "width": ""},
        {"name": 'comments', "class": "", "width": ""},
        {"name": 'date_email_sent', "class": "", "width": ""},
    ]

    # def get_new_object_url(self):
    #     return reverse("whalebrary:resight_new", kwargs=self.kwargs)


# class ResightDetailView(WhalebraryAccessRequired, CommonDetailView):
#     model = models.Resight
#     field_list = [
#         'id',
#         'reported_by',
#         'resight_date',
#         'comments',
#         'date_email_sent',
#
#     ]
#     home_url_name = "whalebrary:index"
#     parent_crumb = {"title": gettext_lazy("Resight List"), "url": reverse_lazy("whalebrary:resight_list")}


class ResightUpdateView(WhalebraryEditRequiredMixin, CommonUpdateView):
    model = models.Resight
    form_class = forms.ResightForm
    template_name = 'whalebrary/form.html'
    cancel_text = _("Cancel")

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Resight record successfully updated for : {my_object}"))
        success_url = reverse_lazy('shared_models:close_me')
        return HttpResponseRedirect(success_url)


class ResightCreateView(WhalebraryEditRequiredMixin, CommonCreateView):
    model = models.Resight
    form_class = forms.ResightForm
    template_name = 'whalebrary/form.html'

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Resight successfully added for : {my_object}"))
        return HttpResponseRedirect(reverse_lazy('shared_models:close_me'))

    def get_initial(self):
        incident = models.Incident.objects.get(pk=self.kwargs['incident'])
        return {
            'incident': incident,
        }


class ResightDeleteView(WhalebraryEditRequiredMixin, CommonPopoutDeleteView):
    model = models.Resight
    delete_protection = False

    ## INCIDENT IMAGE UPLOAD ##


class ImageListView(WhalebraryAdminAccessRequired, CommonFilterView):
    template_name = "whalebrary/image_list.html"
    h1 = "Image List"
    filterset_class = filters.ImageFilter
    home_url_name = "whalebrary:index"
    # new_btn_text = "New File"

    queryset = models.Image.objects.annotate(
        search_term=Concat('id', 'incident__name', 'title', 'image', 'date_uploaded', output_field=TextField()))

    field_list = [
        {"name": 'id', "class": "", "width": ""},
        {"name": 'incident', "class": "", "width": "100px"},
        {"name": 'title', "class": "", "width": ""},
        {"name": 'image', "class": "", "width": "75px"},
        {"name": 'date_uploaded', "class": "", "width": "100px"},

    ]

    # def get_new_object_url(self):
    #     return reverse("whalebrary:file_new", kwargs=self.kwargs)


class ImageCreateView(WhalebraryEditRequiredMixin, CommonCreateView):
    model = models.Image
    template_name = 'whalebrary/image_form_popout.html'
    form_class = forms.ImageForm

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Image successfully added for : {my_object}"))
        return HttpResponseRedirect(reverse_lazy('shared_models:close_me'))

    def get_initial(self):
        incident = models.Incident.objects.get(pk=self.kwargs['incident'])
        return {
            'incident': incident,
        }


class ImageUpdateView(WhalebraryEditRequiredMixin, CommonUpdateView):
    model = models.Image
    template_name = 'whalebrary/image_form_popout.html'
    form_class = forms.ImageForm
    cancel_text = _("Cancel")

    def form_valid(self, form):
        my_object = form.save()
        messages.success(self.request, _(f"Image record successfully updated for : {my_object}"))
        success_url = reverse_lazy('shared_models:close_me')
        return HttpResponseRedirect(success_url)


class ImageDeleteView(WhalebraryEditRequiredMixin, CommonPopoutDeleteView):
    model = models.Image
    delete_protection = False

    ## REPORTS ##


class ReportGeneratorFormView(WhalebraryAccessRequired, CommonFormView):
    template_name = 'whalebrary/report_generator.html'
    h1 = "Please enter the report details:"
    form_class = forms.ReportGeneratorForm

    def get_initial(self):

        try:
            self.kwargs["report_number"]
        except KeyError:
            print("no report")

    def form_valid(self, form):

        report = int(form.cleaned_data["report"])

        try:
            location = int(form.cleaned_data["location"])
        except ValueError:
            location = None
        try:
            item_name = slugify(form.cleaned_data["item_name"])
        except ValueError:
            item_name = None

        if report == 1:
            return HttpResponseRedirect(reverse("whalebrary:report_container", kwargs={
                'location': str(location),
            }))
        elif report == 2:
            return HttpResponseRedirect(reverse("whalebrary:report_sized_item", kwargs={'item_name': item_name}))

        else:
            messages.error(self.request, "Report is not available. Please select another report.")
            return HttpResponseRedirect(reverse("whalebrary:report_generator"))


class ContainerSummaryListView(WhalebraryAccessRequired, CommonListView):
    template_name = 'whalebrary/report_container_summary.html'
    home_url_name = "whalebrary:index"
    parent_crumb = {"title": gettext_lazy("Report Generator"), "url": reverse_lazy("whalebrary:report_generator")}

    def get_queryset(self, **kwargs):
        qs = models.Transaction.objects.filter(location_id=self.kwargs['location'])
        return qs

    def get_h1(self):
        location = models.Location.objects.get(pk=self.kwargs.get("location"))
        h1 = _("Container Summary for ") + f' {str(location)}'
        return h1

    field_list = [
        {"name": 'item', "class": "", "width": ""},
        {"name": 'quantity', "class": "", "width": ""},
        {"name": 'category', "class": "", "width": ""},
        {"name": 'comments', "class": "", "width": ""},
        {"name": 'audits', "class": "", "width": ""},
        {"name": 'tags', "class": "", "width": ""},
    ]

    # field_list = [
    #     {"name": 'tname|{}'.format(gettext_lazy("Item name (size)")), "class": "", "width": ""},
    #     {"name": 'description', "class": "", "width": ""},
    #     {"name": 'note', "class": "", "width": ""},
    #     {"name": 'total_oh_quantity|{}'.format(gettext_lazy("Total on hand quantity")), "class": "", "width": ""},
    #
    # ]


class SizedItemSummaryListView(WhalebraryAccessRequired, CommonListView):
    template_name = 'whalebrary/report_sized_item_summary.html'
    home_url_name = "whalebrary:index"
    # row_object_url_name = "whalebrary:item_detail"
    parent_crumb = {"title": gettext_lazy("Report Generator"), "url": reverse_lazy("whalebrary:report_generator")}
    h1 = "Sized Summary"

    # def get_template_names(self):
    #     # define here if no data is available to get another template
    #     pass

    def get_h2(self):
        h2 = _("For search term ") + f' "{self.kwargs.get("item_name")}"'
        return h2

    def get_queryset(self, **kwargs):
        qs = models.Transaction.objects.filter(item__item_name__iexact=self.kwargs['item_name'])
        return qs

    field_list = [
        {"name": 'item', "class": "", "width": ""},
        {"name": 'quantity', "class": "", "width": ""},
        {"name": 'category', "class": "", "width": ""},
        {"name": 'comments', "class": "", "width": ""},
        {"name": 'audits', "class": "", "width": ""},
        {"name": 'tags', "class": "", "width": ""},
        {"name": 'location', "class": "", "width": ""},
    ]


## PLANNING LINKS ##

class PlanningLinkListView(WhalebraryAdminAccessRequired, CommonListView):
    template_name = "whalebrary/planning_link_list.html"
    model = models.PlanningLink
    h1 = "Planning Link List"
    home_url_name = "whalebrary:index"
    # new_btn_text = "New Planning Link"
    # new_object_url_name = "whalebrary:planning_link_new"

    field_list = [
        {"name": 'id', "class": "", "width": ""},
        {"name": 'year', "class": "", "width": ""},
        {"name": 'client', "class": "", "width": ""},
        {"name": 'description', "class": "", "width": ""},
        {"name": 'link', "class": "", "width": ""},

        ]


class PlanningLinkCreateView(WhalebraryAdminAccessRequired, CommonPopoutCreateView):
    model = models.PlanningLink
    form_class = forms.PlanningLinkForm


class PlanningLinkUpdateView(WhalebraryAdminAccessRequired, CommonPopoutUpdateView):
    model = models.PlanningLink
    form_class = forms.PlanningLinkForm
    template_name = 'whalebrary/form.html'


class PlanningLinkDeleteView(WhalebraryAdminAccessRequired, CommonPopoutDeleteView):
    model = models.PlanningLink
