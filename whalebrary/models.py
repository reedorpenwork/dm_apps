import os
from datetime import timedelta, datetime
from pathlib import Path

from django.contrib.auth.models import User
from django.contrib.auth.models import User as AuthUser
from django.core.validators import MinValueValidator
from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from lib.templatetags.custom_filters import timedelta_duration_days_hours as td

from shared_models.models import LatLongFields, SimpleLookup


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("english name"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("french name"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)


class GearType(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("english name"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("french name"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)


class Owner(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("english name"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("french name"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)


class Size(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("size"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("taille"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)


class Supplier(models.Model):
    supplier_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("supplier"))
    contact_number = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("contact number"))
    email = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("email"))
    website = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("website"))
    comments = models.TextField(blank=True, null=True, verbose_name=_("comments/details"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("supplier_name"))):

            return "{}".format(getattr(self, str(_("supplier_name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.supplier_name)

    def get_absolute_url(self):
        return reverse("whalebrary:supplier_detail", kwargs={"pk": self.id})


class Item(models.Model):
    item_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("name of item"))
    description = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("description"))
    note = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("note"))
    owner = models.ForeignKey(Owner, on_delete=models.DO_NOTHING, related_name="items",
                              verbose_name=_("owner of equipment"))
    size = models.ForeignKey(Size, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="items",
                             verbose_name=_("size (if applicable)"))
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, related_name="items",
                                 verbose_name=_("category of equipment"))
    gear_type = models.ForeignKey(GearType, on_delete=models.DO_NOTHING, related_name="items",
                                  verbose_name=_("type of equipment"))
    suppliers = models.ManyToManyField(Supplier, blank=True, verbose_name=_("suppliers"))

    class Meta:
        unique_together = (('item_name', 'size'),)
        ordering = ["item_name"]

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("item_name"))):

            my_str = "{}".format(getattr(self, str(_("item_name"))))
        # if there is no translated term, just pull from the english field
        else:
            my_str = "{}".format(self.item_name)

        if self.size:
            my_str += f' ({self.size})'
        return my_str

    @property
    def tname(self):
        return str(self)

    @property
    def lent_out_quantities(self):
        """find all category=3 (lent out) transactions"""
        return self.transactions.filter(category=3, return_tracker=False)
        # same as:
        # return Transaction.objects.filter(item=self, category=3)

    def get_oh_quantity(self, location=None):
        """find total quantity for item regardless of location"""
        if not location:
            purchase_qty = sum([item.quantity for item in self.transactions.filter(category__in=[1, 4, 6])])
            removed_quantity = sum([item.quantity for item in self.transactions.filter(category__in=[2, 3, 5])])
            qty = purchase_qty - removed_quantity
        else:
            purchase_qty = sum([item.quantity for item in self.transactions.filter(category__in=[1, 4, 6], location=location)])
            removed_quantity = sum(
                [item.quantity for item in self.transactions.filter(category__in=[2, 3, 5], location=location)])
            qty = purchase_qty - removed_quantity
        return qty

    @property
    def total_oh_quantity(self):
        """find total quantity for item regardless of location"""
        return self.get_oh_quantity()

    @property
    def oh_quantity_by_location(self):
        """find total quantity available for item at each location"""
        location_list = self.transactions.all().values("location").distinct().order_by("location")
        my_dict = dict()
        for l in location_list:
            location = Location.objects.get(pk=l["location"])
            my_dict[location] = self.get_oh_quantity(location)
        return my_dict

    # @property
    # def oh_quantity_by_item(self):
    #     """find total quantity available for location of each item"""
    #     item_list = self.transactions.all().values("item").distinct().order_by("item")
    #     my_dict = dict()
    #     for l in item_list:
    #         item = Item.objects.get(pk=l["item"])
    #         my_dict[item] = self.get_oh_quantity(item)
    #     return my_dict

    @property
    def active_orders(self):
        """find all order that have not been marked received"""
        return self.orders.filter(date_received__isnull=True)

    def get_absolute_url(self):
        return reverse("whalebrary:item_detail", kwargs={"pk": self.id})


class Location(models.Model):
    location = models.CharField(max_length=250, blank=False, null=False, verbose_name=_("location"))
    bin_id = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("bin id"))
    address = models.CharField(max_length=250, blank=False, null=False, verbose_name=_("address"))
    container = models.BooleanField(default=False,
                                    verbose_name=_("is this item a container with more items inside it?"))
    container_space = models.IntegerField(null=True, blank=True,
                                          verbose_name=_("container Space Available (if applicable)"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("location"))):

            my_str = "{}".format(getattr(self, str(_("location"))))
        # if there is no translated term, just pull from the english field
        else:
            my_str = "{}".format(self.location)

        if self.bin_id:
            my_str += f' (bin # {self.bin_id})'
        return my_str

    class Meta:
        ordering = ["location", ]

    def get_absolute_url(self):
        return reverse("whalebrary:location_detail", kwargs={"pk": self.id})


def file_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/item_<id>/<filename>
    return f'whalebrary/{instance.item.item_name}_id{instance.item.id}/{filename}'


class File(models.Model):
    caption = models.CharField(max_length=255, verbose_name=_("caption"))
    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING, related_name="files", verbose_name=_("item"))
    file = models.FileField(upload_to=file_directory_path, verbose_name=_("file"))
    date_uploaded = models.DateTimeField(auto_now=True, editable=False, verbose_name=_("date uploaded"))

    class Meta:
        ordering = ['-date_uploaded']

    def __str__(self):
        return self.caption


@receiver(models.signals.post_delete, sender=File)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


@receiver(models.signals.pre_save, sender=File)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = File.objects.get(pk=instance.pk).file
    except File.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


class Organisation(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("english name"))
    abbrev_name = models.CharField(max_length=255, verbose_name=_("english abbreviated name"))
    nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("french name"))
    abbrev_nom = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("french abbreviated name"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)


class Training(models.Model):
    name = models.CharField(max_length=255)
    nom = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)


class Experience(models.Model):
    EXPERIENCE_LEVEL_CHOICES = (
        ('None', _("No previous experience")),
        ('Novice', _("1-2 Necropsies")),
        ('Intermediate', _("3-5 Necropsies")),
        ('Advanced', _("More than 5 Necropsies")),
    )
    name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("name"))
    nom = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("nom"))
    description_eng = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("english description"))
    description_fra = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("french description"))
    experience = models.CharField(max_length=255, choices=EXPERIENCE_LEVEL_CHOICES, default='None',
                                  verbose_name=_("experience level"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("name"))):

            return "{}".format(getattr(self, str(_("name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.name)

    def get_absolute_url(self):
        return reverse("whalebrary:personnel_detail", kwargs={"pk": self.id})


class Personnel(models.Model):
    first_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("first name"))
    last_name = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("last name"))
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name="people",
                                     verbose_name=_("organisation"), null=True, blank=True)
    email = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("email address"))
    phone = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("phone number"))
    exp_level = models.ForeignKey(Experience, help_text="Novice 1-2 necropsy, Intermediate 3-5, Advanced more than 5",
                                  on_delete=models.DO_NOTHING, related_name="xp",
                                  verbose_name=_("experience level"))
    trainings = models.ManyToManyField(Training, blank=True, verbose_name=_("training"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("first_name"))):

            return "{}".format(getattr(self, str(_("first_name"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.first_name)

    def get_absolute_url(self):
        return reverse("whalebrary:personnel_detail", kwargs={"pk": self.id})


class Species(SimpleLookup):
    name_latin = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("name (latin)"))
    species_code = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("species code"))


class Incident(LatLongFields):
    BOOL_CHOICES = ((True, 'Yes'), (False, 'No'))

    REGION_CHOICES = (
        ("Gulf", "Gulf"),
        ("Mar", "Maritimes"),
        ("NL", "Newfoundland"),
        ("QC", "Quebec"),
    )

    SEX_CHOICES = (
        ("M", "Male"),
        ("F", "Female"),
        ("UnK", "Unknown"),
    )

    AGE_CHOICES = (
        ("N", "Newborn"),
        ("J", "Juvenile"),
        ("A", "Adult"),
        ("UnK", "Unknown"),
    )

    INCIDENT_CHOICES = (
        ("E", "Entangled"),
        ("DF", "DEAD - Floating"),
        ("DB", "DEAD - Beached"),
        ("LS", "LIVE - Stranded"),
    )

    RESPONSE_CHOICES = (
        ("D", "Disentanglement"),
        ("R", "Refloating"),
        ("DE", "Documentation / Examination"),
        ("N", "Necropsy"),
        ("E", "Education"),
        ("O", "Other"),
    )

    name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("incident name"))
    species_count = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("species count"))
    submitted = models.BooleanField(choices=BOOL_CHOICES, blank=True, null=True,
                                    verbose_name=_("incident report submitted by Gulf?"))
    reported_by = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("reported by"))
    first_report = models.DateTimeField(blank=True, null=True, verbose_name=_("date and time first reported"))
    location = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("location"))
    region = models.CharField(max_length=255, null=True, blank=True, choices=REGION_CHOICES, verbose_name=_("region"))
    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name="incidents", verbose_name=_("species"))
    sex = models.CharField(max_length=255, blank=True, null=True, choices=SEX_CHOICES, verbose_name=_("sex"))
    age_group = models.CharField(max_length=255, blank=True, null=True, choices=AGE_CHOICES,
                                 verbose_name=_("age group"))
    incident_type = models.CharField(max_length=255, blank=True, null=True, choices=INCIDENT_CHOICES,
                                     verbose_name=_("type of Incident"))
    gear_presence = models.BooleanField(blank=True, null=True, choices=BOOL_CHOICES, verbose_name=_("gear Presence?"))
    gear_desc = models.CharField(blank=True, null=True, max_length=255, verbose_name=_("gear description"))
    response = models.BooleanField(blank=True, null=True, choices=BOOL_CHOICES, verbose_name=_("was there a response?"))
    response_type = models.CharField(max_length=255, blank=True, null=True, choices=RESPONSE_CHOICES, verbose_name=_("response type"))
    response_by = models.ManyToManyField(Organisation, blank=True, related_name="incidents", verbose_name=_("response by"))
    response_date = models.DateTimeField(blank=True, null=True, verbose_name=_("date and time of response"))
    necropsy = models.BooleanField(blank=True, null=True, choices=BOOL_CHOICES, verbose_name=_("necropsy conducted?"))
    results = models.CharField(blank=True, null=True, max_length=255, verbose_name=_("results"))
    photos = models.BooleanField(blank=True, null=True, choices=BOOL_CHOICES, verbose_name=_("photos?"))
    data_folder = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("data folder"))
    comments = models.TextField(blank=True, null=True, verbose_name=_("comments/details"))
    date_email_sent = models.DateTimeField(blank=True, null=True, verbose_name="date incident emailed")

    @property
    def incident_id(self):
        my_str = ""

        if self.incident_type:
            my_str += f'{self.incident_type}'
        if self.first_report:
            my_str += f'{self.first_report.strftime("%Y%m%d")}'
        if self.species.species_code:
            my_str += f'{self.species.species_code}'
        if self.id:
            my_str += f' (inc.ID #{self.id})'
        return my_str

    @property
    def data_folder_path(self):
        my_path = ""

        if self.data_folder:
            try:
                my_path += fr'{self.data_folder}'
                new_path = my_path.split(':\\')[1]
                drive_path = r'\\glfscidm002\cetacean'
                final_path = drive_path + '\\' + new_path
                return final_path
            except IndexError:
                my_path = "Re-enter drive path"

            # \\glfscidm002\cetacean\MM_DATA_COLLECTION\2021\plane\DFO_SASAIR_CGZWF_ScienceCessna\sGSL_BroadscaleMMSurvey_20210705_ZWF20210705
        else:
            my_path += "N/A"
        return my_path

    def __str__(self):
        if self.incident_id:
            return self.incident_id
        else:
            return "None"

    def get_leaflet_dict(self):
        json_dict = dict(
            type='Feature',
            properties=dict(
                name=self.name,
                id=self.incident_id,
                pk=self.pk,
                type=str(self.get_incident_type_display()), #if this is not filled in this method fails though, need to make separate one for error handling, seems to work making it a string
                species=self.species.name,
                date=str(self.first_report),
            ),
            geometry=dict(type='Point', coordinates=list([self.longitude, self.latitude]))
        )
        return json_dict

    def get_absolute_url(self):
        return reverse("whalebrary:incident_detail", kwargs={"pk": self.id})


class Resight(LatLongFields):
    incident = models.ForeignKey(Incident, on_delete=models.DO_NOTHING, related_name="resights", verbose_name=_("incident"))
    reported_by = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("reported by"))
    resight_date = models.DateTimeField(blank=True, null=True, verbose_name=_("date and time of resight"))
    comments = models.TextField(blank=True, null=True, verbose_name=_("comments/details"))
    date_email_sent = models.DateTimeField(blank=True, null=True, verbose_name="date resight incident emailed")

    def __str__(self):
        my_str = "{}".format(self.id)

        if self.incident.name:
            my_str += f' ({self.incident.name})'
        return my_str

    def get_leaflet_resight_dict(self):
        json_dict = dict(
            type='Feature',
            properties=dict(
                pk=self.pk,
                date=str(self.resight_date),
                comments=self.comments,
            ),
            geometry=dict(type='Point', coordinates=list([self.longitude, self.latitude]))
        )
        return json_dict


def image_directory_path(instance, imagename):
    # image will be uploaded to MEDIA_ROOT/item_<id>/<filename>
    return f'whalebrary/{instance.incident.name}_id{instance.incident.id}/{imagename}'


class Image(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("title"))
    incident = models.ForeignKey(Incident, on_delete=models.DO_NOTHING, related_name="images", verbose_name=_("incident"))
    image = models.ImageField(upload_to=image_directory_path, verbose_name=_("image"))
    date_uploaded = models.DateTimeField(auto_now=True, editable=False, verbose_name=_("date uploaded"))

    class Meta:
        ordering = ['-date_uploaded']

    def __str__(self):
        return self.title


class Audit(models.Model):
    date = models.DateTimeField(default=timezone.now, verbose_name=_("last audited on"))
    last_audited_by = models.ForeignKey(AuthUser, on_delete=models.DO_NOTHING, verbose_name=_("last audited by"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("date"))):

            return "{}".format(getattr(self, str(_("date"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.date)


class Maintenance(models.Model):

    MAINT_CHOICES = (
        (1, "Charging"),
        (2, "Book Inspection"),
        (3, "Other"),
    )

    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING, related_name="maintenances", verbose_name=_("item"))
    maint_type = models.IntegerField(choices=MAINT_CHOICES, verbose_name=_("maintenance type"))
    schedule = models.DurationField(default=timedelta(days=30), verbose_name=_("maintenance schedule"))
    assigned_to = models.ForeignKey(AuthUser, on_delete=models.DO_NOTHING, related_name="assigneds", verbose_name=_("assigned to"))
    comments = models.TextField(blank=True, null=True, verbose_name=_("comments/details"))
    last_maint_by = models.ForeignKey(AuthUser, on_delete=models.DO_NOTHING, related_name="maintainers", verbose_name=_("last maintained by"))
    last_maint_date = models.DateTimeField(blank=True, null=True, verbose_name="date last maintained")

    class Meta:
        ordering = ["last_maint_date"]

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("item"))):

            return "{}".format(getattr(self, str(_("item"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.item.item_name)

    @property
    def days_until_maint(self):
        date_scheduled = self.last_maint_date + self.schedule
        today = datetime.now(timezone.utc)
        time_remaining = date_scheduled - today
        return td(time_remaining)

    @property
    def overdue(self):
        date_scheduled = self.last_maint_date + self.schedule
        today = datetime.now(timezone.utc)
        if date_scheduled >= today:
            return False
        else:
            return True


class Tag(models.Model):
    tag = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("tag"))
    description = models.TextField(blank=True, null=True, verbose_name=_("description"))

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("tag"))):

            return "{}".format(getattr(self, str(_("tag"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.tag)


class TransactionCategory(models.Model):
    CATEGORY_CHOICES = (
        (1, "Purchase"),
        (2, "Use"),
        (3, "Lend"),
        (4, "Return"),
        (5, "Transfer Out"),
        (6, "Transfer In"),
    )

    type = models.IntegerField(choices=CATEGORY_CHOICES, verbose_name=_("type"))
    description = models.CharField(max_length=255, null=True, verbose_name=_("description"))

    def __str__(self):
        return "{}".format(self.get_type_display())


class Transaction(models.Model):
    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING, related_name="transactions", verbose_name=_("item"))
    quantity = models.FloatField(verbose_name=_("quantity"), validators=[MinValueValidator(1)])
    category = models.ForeignKey(TransactionCategory, on_delete=models.DO_NOTHING, related_name="transactions",
                                 verbose_name=_("transaction category"))
    # track which 'lent' transactions have been voided/returned
    return_tracker = models.BooleanField(default=False, verbose_name=_("Returned"))
    # can use for who lent to, etc
    comments = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("comments"))
    # auditing
    audits = models.ManyToManyField(Audit, blank=True, verbose_name=_("audits"))
    # location of quantities taken/used/received
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING, related_name="transactions",
                                 verbose_name=_("location stored"))
    # use "tag" field with M2M to track things of interest instead of "incident", "project code" etc.
    tags = models.ManyToManyField(Tag, blank=True, related_name="transactions", verbose_name=_("tags"))
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    created_by = models.ForeignKey(AuthUser, on_delete=models.DO_NOTHING)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):

        # check to see if a french value is given
        if getattr(self, str(_("item"))):

            my_str = "{}".format(getattr(self, str(_("item"))))
        # if there is no translated term, just pull from the english field
        else:
            my_str = "{}".format(self.item)

        if self.quantity:
            return '{} - {}'.format(self.quantity, my_str)

        else:
            return '{}'.format(my_str)

    def get_absolute_url(self):
        return reverse("whalebrary:transaction_detail", kwargs={"pk": self.id})

    # from https://github.com/ccnmtl/dmt/blob/master/dmt/main/models.py
    # def reassign(self, user, assigned_to, comment):
    #     self.assigned_user = assigned_to.user
    #     self.save()
    #     e = Events.objects.create(
    #         status="OPEN",
    #         event_date_time=timezone.now(),
    #         item=self)
    #     Comment.objects.create(
    #         event=e,
    #         username=user.username,
    #         author=user.user,
    #         comment="<b>Reassigned to %s</b><br />\n%s" % (
    #             assigned_to.fullname, comment),
    #         add_date_time=timezone.now())
    #     self.add_subscriber(assigned_to)
    #
    # def get_fullname(self):
    #     return self.item or self.id


class Order(models.Model):
    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING, related_name="orders", verbose_name=_("item"))
    quantity = models.IntegerField(null=True, blank=True, verbose_name=_("quantity"))
    cost = models.FloatField(blank=True, null=True, verbose_name=_("order cost"))
    date_ordered = models.DateTimeField(default=timezone.now, verbose_name=_("order date"))
    date_received = models.DateTimeField(blank=True, null=True, verbose_name=_("received date"))
    transaction = models.OneToOneField(Transaction, blank=True, null=True, on_delete=models.DO_NOTHING,
                                       related_name="orders",
                                       verbose_name=_("transaction"))

    class Meta:
        ordering = ["-date_ordered"]

    def __str__(self):
        # check to see if a french value is given
        if getattr(self, str(_("id"))):

            return "{}".format(getattr(self, str(_("id"))))
        # if there is no translated term, just pull from the english field
        else:
            return "{}".format(self.id)

    @property
    def trans_id(self):
        if self.transaction:
            my_str = "# {}".format(self.transaction_id)
            return my_str
        else:
            no_str = "---"
            return no_str


class PlanningLink(models.Model):
    year = models.IntegerField(verbose_name=_("planning year"))
    client = models.CharField(max_length=250, verbose_name=_("client"))
    description = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("description"))
    link = models.URLField(max_length=250, blank=True, null=True, verbose_name=_("link"))

    def __str__(self):
        return '{} ({})'.format(self.client, self.year)
