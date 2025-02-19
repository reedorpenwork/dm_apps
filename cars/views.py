import datetime
import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Value, TextField
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.timezone import make_aware, get_current_timezone
from django.utils.translation import gettext_lazy, gettext as _

from cars import models, forms, filters, emails, reports
from cars.mixins import CarsBasicMixin, SuperuserOrAdminRequiredMixin, CarsNationalAdminRequiredMixin, CanModifyVehicleRequiredMixin, \
    CanModifyReservationRequiredMixin, CarsAdminRequiredMixin
from cars.utils import get_dates_from_range, is_dt_intersection, can_modify_vehicle
from dm_apps.context_processor import my_envr
from lib.functions.custom_functions import listrify
from shared_models.views import CommonTemplateView, CommonFormsetView, CommonHardDeleteView, CommonDeleteView, CommonDetailView, CommonUpdateView, \
    CommonFilterView, CommonCreateView, CommonFormView, CommonListView


class IndexTemplateView(CarsBasicMixin, CommonTemplateView):
    h1 = "home"
    active_page_name_crumb = "home"
    template_name = 'cars/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["requests_waiting"] = models.Reservation.objects.filter(vehicle__custodian=self.request.user, status=1).count()
        return context


class FAQListView(CarsBasicMixin, CommonFilterView):
    h1 = " "
    active_page_name_crumb = "FAQ"
    template_name = 'cars/faq.html'
    model = models.FAQ
    filterset_class = filters.FAQFilter

    def get_queryset(self):
        qs = self.model.objects.annotate(search=Concat(
            'question_en', Value(" "),
            'question_fr', Value(" "),
            'answer_en', Value(" "),
            'answer_fr', output_field=TextField()))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["refs"] = models.ReferenceMaterial.objects.all()
        return context

# REFERENCE TABLES #
####################

class CarsUserFormsetView(SuperuserOrAdminRequiredMixin, CommonFormsetView):
    template_name = 'cars/formset.html'
    h1 = "Manage Cars Users"
    queryset = models.CarsUser.objects.all()
    formset_class = forms.CarsUserFormset
    success_url_name = "cars:manage_cars_users"
    delete_url_name = "cars:delete_cars_user"
    container_class = "container bg-light curvy"


class CarsUserHardDeleteView(SuperuserOrAdminRequiredMixin, CommonHardDeleteView):
    model = models.CarsUser
    success_url = reverse_lazy("cars:manage_cars_users")


class VehicleTypeFormsetView(CarsNationalAdminRequiredMixin, CommonFormsetView):
    template_name = 'cars/formset.html'
    h1 = "Manage Vehicle Types"
    queryset = models.VehicleType.objects.all()
    formset_class = forms.VehicleTypeFormset
    success_url_name = "cars:manage_vehicle_types"
    home_url_name = "cars:index"
    delete_url_name = "cars:delete_vehicle_type"


class VehicleTypeHardDeleteView(CarsNationalAdminRequiredMixin, CommonHardDeleteView):
    model = models.VehicleType
    success_url = reverse_lazy("cars:manage_vehicle_types")


class LocationFormsetView(CarsAdminRequiredMixin, CommonFormsetView):
    template_name = 'cars/formset.html'
    h1 = "Manage Locations"
    queryset = models.Location.objects.all()
    formset_class = forms.LocationFormset
    success_url_name = "cars:manage_locations"
    home_url_name = "cars:index"
    delete_url_name = "cars:delete_location"


class LocationHardDeleteView(CarsAdminRequiredMixin, CommonHardDeleteView):
    model = models.Location
    success_url = reverse_lazy("cars:manage_locations")


class VehicleFormsetView(CarsNationalAdminRequiredMixin, CommonFormsetView):
    template_name = 'cars/formset.html'
    h1 = "Manage Vehicles"
    queryset = models.Vehicle.objects.all()
    formset_class = forms.VehicleFormset
    success_url_name = "cars:manage_vehicles"
    home_url_name = "cars:index"
    delete_url_name = "cars:delete_vehicle"
    container_class = "container-fluid"


class VehicleHardDeleteView(CarsNationalAdminRequiredMixin, CommonHardDeleteView):
    model = models.Vehicle
    success_url = reverse_lazy("cars:manage_vehicles")


class FAQFormsetView(CarsNationalAdminRequiredMixin, CommonFormsetView):
    template_name = 'cars/formset.html'
    h1 = "Manage FAQs"
    queryset = models.FAQ.objects.all()
    formset_class = forms.FAQFormset
    success_url_name = "cars:manage_faqs"
    home_url_name = "cars:index"
    delete_url_name = "cars:delete_faq"


class FAQHardDeleteView(CarsNationalAdminRequiredMixin, CommonHardDeleteView):
    model = models.FAQ
    success_url = reverse_lazy("cars:manage_faqs")


class VehicleFinder(CarsBasicMixin, CommonFormView):
    template_name = 'cars/vehicle_finder.html'
    form_class = forms.VehicleFinderForm
    h1 = gettext_lazy("Find a Vehicle")

    def get_initial(self):
        qp = self.request.GET
        payload = dict()
        if qp.get("start_date") and qp.get("end_date"):
            payload["date_range"] = f"{qp.get('start_date')} to {qp.get('end_date')}"
        if qp.get("vehicle_type"):
            payload["vehicle_type"] = qp.get('vehicle_type')
        if qp.get("section"):
                payload["vehicle_section"] = qp.get('section')
        if qp.get("max_passengers__gte"):
            payload["no_passengers"] = qp.get('max_passengers__gte')
        if qp.get("location"):
            payload["location"] = qp.get('location')
        if qp.get("id"):
            payload["vehicle"] = qp.get('id')
        return payload

    def form_valid(self, form):

        # let's see what we got
        date_range = form.cleaned_data["date_range"]
        # region = form.cleaned_data["region"]
        location = form.cleaned_data["location"]
        vehicle_type = form.cleaned_data["vehicle_type"]
        section = form.cleaned_data["vehicle_section"]
        vehicle = form.cleaned_data["vehicle"]
        no_passengers = form.cleaned_data["no_passengers"]

        dates = get_dates_from_range(date_range)
        start_date = dates[0]
        end_date = dates[1]
        query_string = f"?start_date={start_date.strftime('%Y-%m-%d')}&end_date={end_date.strftime('%Y-%m-%d')}&"

        if location:
            query_string += f"location={location.id}&"
        if vehicle_type:
            query_string += f"vehicle_type={vehicle_type.id}&"
        if section:
            query_string += f"section={section.id}&"
        if vehicle:
            query_string += f"id={vehicle.id}&"
        if no_passengers:
            query_string += f"max_passengers__gte={no_passengers}&"

        good_vehicles = [v.id for v in models.Vehicle.objects.all()]
        for r in models.Reservation.objects.filter(status=10, is_complete=False):
            if is_dt_intersection(r.start_date, r.end_date, start_date, end_date):
                # then we have to remove the vehicle
                try:
                    good_vehicles.remove(r.vehicle_id)
                except ValueError:
                    pass
        query_string += f"ids={listrify(good_vehicles, separator=',')}&"

        return HttpResponseRedirect(reverse("cars:vehicle_list") + query_string)


# VEHICLES #
###########

class VehicleListView(CarsBasicMixin, CommonFilterView):
    template_name = 'cars/vehicle_list.html'
    filterset_class = filters.VehicleFilter
    new_object_url = reverse_lazy("cars:vehicle_new")
    row_object_url_name = row_ = "cars:vehicle_detail"
    paginate_by = 10

    def get_queryset(self):
        qs = models.Vehicle.objects.annotate(search=Concat(
            'reference_number', Value(" "),
            'make', Value(" "),
            'model', output_field=TextField()))

        qp = self.request.GET
        if qp.get("personalized"):
            return self.request.user.vehicles.all()
        elif qp.get("ids"):
            if qp.get("ids") == "None":
                ids = []
            else:
                ids = qp.get("ids").split(",")
            return qs.filter(id__in=ids)
        else:
            return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qp = self.request.GET
        if qp.get("personalized"):
            context["personalized"] = True
            context["filter"] = None
            context["paginate_by"] = None
        if qp.get("ids"):
            context["h1"] = _("Your Search Results")
            context["filter"] = None
            context["paginate_by"] = None
            context["new_object_button"] = None
        return context


class VehicleUpdateView(CanModifyVehicleRequiredMixin, CommonUpdateView):
    model = models.Vehicle
    form_class = forms.VehicleForm
    template_name = 'cars/form.html'
    home_url_name = "cars:index"
    grandparent_crumb = {"title": gettext_lazy("Vehicles"), "url": reverse_lazy("cars:vehicle_list")}
    is_multipart_form_data = True

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("cars:vehicle_detail", args=[self.get_object().id])}


class VehicleCreateView(CarsBasicMixin, CommonCreateView):
    model = models.Vehicle
    form_class = forms.VehicleForm
    success_url = reverse_lazy('cars:vehicle_list')
    template_name = 'cars/form.html'
    home_url_name = "cars:index"
    parent_crumb = {"title": gettext_lazy("Vehicles"), "url": reverse_lazy("cars:vehicle_list")}
    is_multipart_form_data = True

    def get_initial(self):
        return dict(custodian=self.request.user)


class VehicleDetailView(CarsBasicMixin, CommonDetailView):
    model = models.Vehicle
    template_name = 'cars/vehicle_detail.html'
    home_url_name = "cars:index"
    parent_crumb = {"title": gettext_lazy("Vehicles"), "url": reverse_lazy("cars:vehicle_list")}
    field_list = [
        "location.region|{}".format(_("region")),
        "location.full_address|{}".format(_("location")),
        "custodian",
        "section",
        "vehicle_type",
        "reference_number",
        "make",
        "model",
        "year",
        "max_passengers",
        "is_active",
        "comments",
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_modify"] = can_modify_vehicle(self.request.user, self.get_object())
        return context


class VehicleDeleteView(CanModifyVehicleRequiredMixin, CommonDeleteView):
    model = models.Vehicle
    success_url = reverse_lazy('cars:vehicle_list')
    success_message = 'The functional group was successfully deleted!'
    template_name = 'cars/confirm_delete.html'
    delete_protection = False
    grandparent_crumb = {"title": gettext_lazy("Vehicles"), "url": reverse_lazy("cars:vehicle_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("cars:vehicle_detail", args=[self.get_object().id])}


class VehicleCalendarView(CarsBasicMixin, CommonFilterView):
    model = models.Vehicle
    template_name = 'cars/calendar.html'
    home_url_name = "cars:index"
    h1 = gettext_lazy("Vehicle Calendar")
    container_class = "container-fluid"
    filterset_class = filters.VehicleFilter

    def get_queryset(self):
        qs = models.Vehicle.objects.annotate(search=Concat(
            'reference_number', Value(" "),
            'make', Value(" "),
            'model', output_field=TextField()))
        return qs


# RESERVATIONS #
################

class ReservationListView(CarsBasicMixin, CommonFilterView):
    template_name = 'cars/list.html'
    filterset_class = filters.SimpleReservationFilter
    row_object_url_name = row_ = "cars:rsvp_detail"
    paginate_by = 10
    field_list = [
        {"name": 'status', "class": "", "width": ""},
        {"name": 'start_date', "class": "", "width": ""},
        {"name": 'end_date', "class": "", "width": ""},
        {"name": 'destination', "class": "", "width": ""},
        {"name": 'vehicle', "class": "", "width": ""},
        {"name": 'primary_driver', "class": "", "width": ""},
        {"name": 'other_drivers', "class": "", "width": ""},
    ]

    def get_queryset(self):
        qp = self.request.GET
        if qp.get("personalized"):
            return self.request.user.vehicle_reservations.all()
        elif qp.get("my_vehicles"):
            return models.Reservation.objects.filter(vehicle__custodian=self.request.user, status=1).order_by("status")
        return models.Reservation.objects.all()

    def get_h1(self):
        qp = self.request.GET
        if qp.get("personalized"):
            return _("Your Reservations")
        elif qp.get("my_vehicles"):
            return _("Pending Requests for Your Vehicles")
        return _("Reservations")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qp = self.request.GET
        if qp.get("personalized"):
            context["personalized"] = True
            context["filter"] = None
            context["paginate_by"] = None
        elif qp.get("my_vehicles"):
            context["filter"] = None
            context["paginate_by"] = None
        return context


class ReservationUpdateView(CanModifyReservationRequiredMixin, CommonUpdateView):
    model = models.Reservation
    form_class = forms.ReservationForm
    template_name = 'cars/form.html'
    home_url_name = "cars:index"

    def get_initial(self):
        qp = self.request.GET
        payload = dict()
        rsvp = self.get_object()
        payload["start_date"] = rsvp.start_date.strftime("%Y-%m-%dT%H:%M")
        payload["end_date"] = rsvp.end_date.strftime("%Y-%m-%dT%H:%M")
        return payload

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("cars:rsvp_detail", args=[self.get_object().id])}

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        return super().form_valid(form)


class ReservationCreateView(CarsBasicMixin, CommonCreateView):
    model = models.Reservation
    form_class = forms.ReservationForm
    template_name = 'cars/form.html'
    home_url_name = "cars:index"

    def get_initial(self):
        qp = self.request.GET
        payload = dict(primary_driver=self.request.user)
        if qp.get("start_date"):
            dt = make_aware(datetime.datetime.strptime(f'{qp.get("start_date")} 8:00', "%Y-%m-%d %H:%M"), get_current_timezone())
            payload["start_date"] = dt.strftime("%Y-%m-%dT%H:%M")

        if qp.get("end_date"):
            dt = make_aware(datetime.datetime.strptime(f'{qp.get("end_date")} 16:00', "%Y-%m-%d %H:%M"), get_current_timezone())
            payload["end_date"] = dt.strftime("%Y-%m-%dT%H:%M")

        if qp.get("vehicle"):
            payload["vehicle"] = qp.get('vehicle')

        return payload

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        obj = form.save(commit=True)

        if obj.primary_driver != obj.vehicle.custodian:
            # send the email object
            email = emails.RSVPEmail(self.request, obj)
            email.send()
            self.success_url = reverse("cars:vehicle_detail", args=[obj.vehicle.id])
        else:
            self.success_url = reverse("cars:rsvp_detail", args=[obj.id])
        return super().form_valid(form)

class ReservationDetailView(CarsBasicMixin, CommonDetailView):
    model = models.Reservation
    template_name = 'cars/rsvp_detail.html'
    home_url_name = "cars:index"
    # parent_crumb = {"title": gettext_lazy("Reservations"), "url": reverse_lazy("cars:rsvp_list")}
    field_list = [
        "status",
        "vehicle",
        "vehicle.custodian|{}".format(_("custodian")),
        "vehicle.section|{}".format(_("section")),
        "destination",
        "primary_driver",
        "arrival_departure|{}".format(gettext_lazy("Arrival/departure")),
        "other_drivers",
        "comments",
        # "surrounding_rsvps|{}".format(gettext_lazy("Surrounding RSVPs")),

    ]


class ReservationDeleteView(CanModifyReservationRequiredMixin, CommonDeleteView):
    model = models.Reservation
    success_url = reverse_lazy('cars:rsvp_list')
    success_message = 'The functional group was successfully deleted!'
    template_name = 'cars/confirm_delete.html'

    # grandparent_crumb = {"title": gettext_lazy("Reservations"), "url": reverse_lazy("cars:rsvp_list")}

    def get_parent_crumb(self):
        return {"title": self.get_object(), "url": reverse_lazy("cars:rsvp_detail", args=[self.get_object().id])}


def rsvp_action(request, pk, action):
    rsvp = get_object_or_404(models.Reservation, pk=pk)
    if action == "accept":
        rsvp.status = 10
        rsvp.save()
        email = emails.ApprovedEmail(request, rsvp)
        email.send()
    elif action == "deny":
        rsvp.status = 20
        rsvp.save()
        email = emails.DeniedEmail(request, rsvp)
        email.send()
    elif action == "reset":
        rsvp.status = 1
        rsvp.save()
    elif action == "field":
        rsvp.status = 30
        rsvp.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# REFERENCE MATERIALS
#####################

class ReferenceMaterialListView(CarsNationalAdminRequiredMixin, CommonListView):
    template_name = "cars/list.html"
    model = models.ReferenceMaterial
    field_list = [
        {"name": "tname|{}".format(gettext_lazy("name")), "class": "", "width": ""},
        {"name": "turl|{}".format(gettext_lazy("URL")), "class": "", "width": ""},
        {"name": "tfile|{}".format(gettext_lazy("File")), "class": "", "width": ""},
        {"name": "created_at", "class": "", "width": ""},
        {"name": "updated_at", "class": "", "width": ""},
    ]
    new_object_url_name = "cars:ref_mat_new"
    row_object_url_name = "cars:ref_mat_edit"
    home_url_name = "cars:index"
    h1 = gettext_lazy("Reference Materials")
    container_class = "container curvy"


class ReferenceMaterialUpdateView(CarsNationalAdminRequiredMixin, CommonUpdateView):
    model = models.ReferenceMaterial
    form_class = forms.ReferenceMaterialForm
    home_url_name = "cars:index"
    parent_crumb = {"title": _("Reference Materials"), "url": reverse_lazy("cars:ref_mat_list")}
    template_name = "cars/form.html"
    is_multipart_form_data = True
    container_class = "container curvy"

    def get_delete_url(self):
        return reverse("cars:ref_mat_delete", args=[self.get_object().id])


class ReferenceMaterialCreateView(CarsNationalAdminRequiredMixin, CommonCreateView):
    model = models.ReferenceMaterial
    form_class = forms.ReferenceMaterialForm
    home_url_name = "cars:index"
    parent_crumb = {"title": _("Reference Materials"), "url": reverse_lazy("cars:ref_mat_list")}
    template_name = "cars/form.html"
    is_multipart_form_data = True
    container_class = "container curvy"


class ReferenceMaterialDeleteView(CarsNationalAdminRequiredMixin, CommonDeleteView):
    model = models.ReferenceMaterial
    success_url = reverse_lazy('cars:ref_mat_list')
    home_url_name = "cars:index"
    parent_crumb = {"title": _("Reference Materials"), "url": reverse_lazy("cars:ref_mat_list")}
    template_name = "cars/confirm_delete.html"
    delete_protection = False
    container_class = "container curvy"




# REPORTS #
###########

class ReportSearchFormView(CarsAdminRequiredMixin, CommonFormView):
    template_name = 'cars/report_search.html'
    form_class = forms.ReportSearchForm
    h1 = gettext_lazy("Reports")
    home_url_name = "cars:index"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        report = int(form.cleaned_data["report"])
        if report == 1:
            return HttpResponseRedirect(reverse("cars:vehicle_report"))
        else:
            messages.error(self.request, "Report is not available. Please select another report.")
            return HttpResponseRedirect(reverse("scuba:reports"))




@login_required()
def vehicle_report(request):
    qp = request.GET
    # fiscal_year = qp.get("fiscal_year") if qp.get("fiscal_year") and qp.get("fiscal_year") != "None" else None

    # get the vehicle list
    qs = models.Vehicle.objects.all()

    site_url = my_envr(request)["SITE_FULL_URL"]
    file_url = reports.generate_vehicle_report(qs, site_url)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            # fy = get_object_or_404(FiscalYear, pk=year) if year else "all years"
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; filename="vehicles.xlsx"'
            return response
    raise Http404

