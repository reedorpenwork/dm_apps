from django.contrib.auth.models import User
from django.db import models
# Create your models here.
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, gettext
from markdown import markdown

from dm_apps.utils import get_timezone_time
from shared_models.models import SimpleLookup, Region, MetadataFields, UnilingualSimpleLookup, LatLongFields

YES_NO_CHOICES = [(True, _("Yes")), (False, _("No")), ]


class CarsUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cars_user", verbose_name=_("DM Apps user"))
    region = models.ForeignKey(Region, verbose_name=_("regional administrator?"), related_name="cars_users", on_delete=models.CASCADE, blank=True,
                               null=True)
    is_admin = models.BooleanField(default=False, verbose_name=_("app administrator?"), choices=YES_NO_CHOICES)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        ordering = ["-is_admin", "user__first_name", ]


class VehicleType(SimpleLookup):
    pass


class Location(SimpleLookup, LatLongFields):
    region = models.ForeignKey(Region, on_delete=models.DO_NOTHING, related_name="vehicle_locations")
    address = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("address"))
    city = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("city"))
    postal_code = models.CharField(max_length=7, blank=True, null=True, verbose_name=_("postal code"))
    province = models.CharField(max_length=7, blank=True, null=True, verbose_name=_("postal code"))

    def get_tname(self):
        mystr = super().get_tname()
        mystr += f" ({self.region})"
        return mystr

    @property
    def full_address(self):
        # initial my_str with either address or None
        if self.address:
            my_str = self.address
        else:
            my_str = ""

        # add city
        if self.city:
            if my_str:
                my_str += "<br>"
            my_str += self.city

        # add province abbrev.
        if self.province:
            if my_str:
                my_str += "<br>"
            my_str += self.province

        # add postal code
        if self.postal_code:
            if my_str:
                my_str += "<br>"
            my_str += self.postal_code

        # add postal code
        if self.get_point():
            if my_str:
                my_str += "<br>"
            label = gettext("view map")
            my_str += f'<span class="mdi mdi-map-marker text-danger lead"></span> <a target="_blank" href="https://www.google.com/maps/search/?api=1&query={self.latitude},{self.longitude}">{label}</a>'

        return mark_safe(my_str)


def img_file_name(instance, filename):
    img_name = 'cars/{}_{}'.format(instance.id, filename)
    return img_name


class Vehicle(MetadataFields):
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING, related_name="vehicles")
    custodian = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="vehicles")
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.DO_NOTHING, related_name="vehicles")
    reference_number = models.CharField(max_length=50, verbose_name=_("reference number"), unique=True)
    make = models.CharField(max_length=255, verbose_name=_("make"))
    model = models.CharField(max_length=255, verbose_name=_("model"))
    year = models.PositiveIntegerField(verbose_name=_("year"))
    max_passengers = models.PositiveIntegerField(verbose_name=_("max passengers"))
    is_active = models.BooleanField(default=True, verbose_name=_("is in commission?"), choices=YES_NO_CHOICES,
                                    help_text=_("Vehicles that are not in commission will not show up in the reservation list"))
    comments = models.TextField(verbose_name=_("comments"), blank=True, null=True)
    thumbnail = models.ImageField(blank=True, null=True, upload_to=img_file_name, verbose_name=_("thumbnail"))

    class Meta:
        ordering = ["reference_number"]

    def __str__(self):
        return f"{self.year} {self.make} {self.model} ({self.reference_number})"

    @property
    def smart_image(self):
        if self.thumbnail.name:
            return self.thumbnail.url
        else:
            return static('cars/no-image-icon.png')

    def get_absolute_url(self):
        return reverse('cars:vehicle_detail', kwargs={'pk': self.id})


class Reservation(MetadataFields):
    status_choices = (
        (1, "Tentative"),
        (10, "Approved"),
        (20, "Denied"),
        (30, "Field Season"),
    )

    vehicle = models.ForeignKey(Vehicle, on_delete=models.DO_NOTHING, blank=True, verbose_name=_("vehicle"), related_name="reservations")
    primary_driver = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name=_("primary driver"), related_name="vehicle_reservations", blank=True)
    start_date = models.DateTimeField(verbose_name=_("departure date"))
    end_date = models.DateTimeField(verbose_name=_("return date"))
    destination = models.CharField(max_length=255, blank=False, null=True, verbose_name=_("destination"))
    other_drivers = models.ManyToManyField(User, blank=True, verbose_name=_("other drivers"))
    comments = models.TextField(blank=True, null=True, verbose_name=_("additional comments"))

    # non-editable
    status = models.IntegerField(choices=status_choices, default=1, editable=False)
    is_complete = models.BooleanField(default=False, editable=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.is_complete = timezone.now() > self.end_date

    def get_absolute_url(self):
        return reverse('cars:rsvp_detail', kwargs={'pk': self.id})

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return gettext("Reservation for {car} by {user}").format(car=self.vehicle, user=self.primary_driver)

    @property
    def arrival_departure(self):
        return mark_safe(_("{arrival} &rarr; {departure}").format(
            arrival=get_timezone_time(self.start_date).strftime("%Y-%m-%d %H:%M"),
            departure=get_timezone_time(self.end_date).strftime("%Y-%m-%d %H:%M"),
        ))


class FAQ(models.Model):
    question_en = models.TextField(blank=True, null=True, verbose_name=_("question (en)"))
    question_fr = models.TextField(blank=True, null=True, verbose_name=_("question (fr)"))
    answer_en = models.TextField(blank=True, null=True, verbose_name=_("answer (en)"))
    answer_fr = models.TextField(blank=True, null=True, verbose_name=_("answer (fr)"))

    class Meta:
        ordering = [_('question_en'), "id"]

    @property
    def tquestion(self):
        # check to see if a french value is given
        if getattr(self, str(_("question_en"))):
            my_str = "{}".format(getattr(self, str(_("question_en"))))
        # if there is no translated term, just pull from the english field
        else:
            my_str = self.question_en
        return my_str

    @property
    def tanswer(self):
        # check to see if a french value is given
        if getattr(self, str(_("answer_en"))):
            my_str = "{}".format(getattr(self, str(_("answer_en"))))
        # if there is no translated term, just pull from the english field
        else:
            my_str = self.answer_en
        return markdown(my_str)
