from django.contrib import auth
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q, Sum
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from markdown import markdown

from lib.functions.custom_functions import listrify
from lib.templatetags.custom_filters import percentage
from shared_models import models as shared_models
from shared_models.models import MetadataFields, LatLongFields, UnilingualSimpleLookup

YES_NO_CHOICES = (
    (True, "Yes"),
    (False, "No"),
)

NULL_YES_NO_CHOICES = (
    (None, _("---------")),
    (1, _("Yes")),
    (0, _("No")),
)


class GRAISUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="grais_user", verbose_name=_("DM Apps user"))
    is_admin = models.BooleanField(default=False, verbose_name=_("app administrator?"), choices=YES_NO_CHOICES)
    is_crud_user = models.BooleanField(default=False, verbose_name=_("CRUD permissions?"), choices=YES_NO_CHOICES)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        ordering = ["-is_admin", "user__first_name", ]


# Create your models here.
class Sampler(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=25, blank=True, null=True)
    organization = models.CharField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    def get_absolute_url(self):
        return reverse('grais:person_detail', kwargs={'pk': self.id})

    class Meta:
        ordering = ['first_name', 'last_name']

    @property
    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name)


class Station(MetadataFields, LatLongFields):
    station_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("name"))
    province = models.ForeignKey(shared_models.Province, on_delete=models.DO_NOTHING, related_name='stations')
    depth = models.FloatField(blank=True, null=True, verbose_name=_("depth (m)"))
    site_desc = models.TextField(blank=True, null=True, verbose_name=_("site description"))
    last_modified_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False)
    contact_information = models.TextField(blank=True, null=True, verbose_name=_("contact information"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("general notes"))

    def __str__(self):
        return "{}, {}".format(self.station_name, self.province.abbrev_eng)

    def get_absolute_url(self):
        return reverse('grais:station_detail', kwargs={'pk': self.id})

    class Meta:
        ordering = ['station_name']

    @property
    def sample_count(self):
        return self.samples.count()

    @property
    def contact_information_html(self):
        if self.contact_information:
            return markdown(self.contact_information)

    @property
    def notes_html(self):
        if self.notes:
            return markdown(self.notes)
    
    @property
    def years(self):
        return listrify([item.get("season") for item in self.samples.order_by("season").values("season").distinct()])

class Species(MetadataFields):
    # choices for epibiont_type
    EPIBIONT_TYPE_CHOICES = (
        (None, "-----"),
        ('ses', "sessile"),
        ('mob', "mobile"),
    )

    common_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("common name (English)"))
    common_name_fra = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("common name (French)"))
    scientific_name = models.CharField(max_length=255, blank=True, null=True)
    abbrev = models.CharField(max_length=255, blank=True, null=True, verbose_name="abbreviation", unique=True)
    epibiont_type = models.CharField(max_length=10, blank=True, null=True, choices=EPIBIONT_TYPE_CHOICES)
    tsn = models.IntegerField(blank=True, null=True, verbose_name="Taxonomic Serial Number")
    aphia_id = models.IntegerField(blank=True, null=True, verbose_name="AphiaID")
    color_morph = models.BooleanField(verbose_name="Has color morph")
    invasive = models.BooleanField(verbose_name="is invasive?")
    # biofouling = models.BooleanField()
    green_crab_monitoring = models.BooleanField(default=False, verbose_name="targeted species in Green Crab Monitoring Program?")
    last_modified_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False)

    @property
    def choice_display(self):
        return f"{self.common_name} / {self.common_name_fra} / {self.scientific_name}"

    @property
    def tname(self):
        if self.common_name or self.common_name_fra:
            if getattr(self, str(_("common_name"))):
                my_str = "{}".format(getattr(self, str(_("common_name"))))
            # if there is no translated term, just pull from the english field
            else:
                my_str = "{}".format(self.common_name)
            return my_str

    @property
    def name_plaintext(self):
        if self.common_name or self.common_name_fra:
            return f"{self.tname} ({self.scientific_name})" if self.scientific_name else self.tname
        else:
            return self.scientific_name

    class Meta:
        ordering = ['common_name']
        verbose_name_plural = _("Species")

    def get_absolute_url(self):
        return reverse('grais:species_detail', kwargs={'pk': self.id})

    @property
    def tcommon(self):
        # check to see if a french value is given
        if getattr(self, str(_("common_name"))):
            my_str = f'{getattr(self, str(_("common_name")))}'
        # if there is no translated term, just pull from the english field
        else:
            my_str = self.common_name
        return my_str

    def __str__(self):
        return self.tcommon if self.tcommon else f"species {self.id}"

    @property
    def full_name(self):
        return "{} (<em>{}</em>)".format(self.common_name, self.scientific_name)

    @property
    def formatted_scientific(self):
        return f"<em>{self.scientific_name}</em>"


class Sample(MetadataFields):
    sample_type_choices = (
        ('first', "first"),
        ('second', "second"),
        ('full', 'full'),
    )

    station = models.ForeignKey(Station, related_name='samples', on_delete=models.DO_NOTHING)
    sample_type = models.CharField(max_length=10, default='full', choices=sample_type_choices, verbose_name="sample type")
    date_deployed = models.DateTimeField()
    date_retrieved = models.DateTimeField(blank=True, null=True)
    days_deployed = models.IntegerField(blank=True, null=True)
    samplers = models.ManyToManyField(Sampler, verbose_name=_("sampler(s)"))
    old_substn_id = models.IntegerField(blank=True, null=True)
    species = models.ManyToManyField(Species, through='SampleSpecies')
    season = models.IntegerField(null=True, blank=True)
    last_modified = models.DateTimeField(blank=True, null=True, editable=False)
    last_modified_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        self.season = self.date_deployed.year
        if self.date_retrieved != None:
            self.days_deployed = (self.date_retrieved - self.date_deployed).days
        self.last_modified = timezone.now()

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('grais:sample_detail', kwargs={'pk': self.id})

    def __str__(self):
        return f"Sample {self.id} ({self.get_sample_type_display()})"

    @property
    def weeks_deployed(self):
        if self.days_deployed != None:
            return str(round(self.days_deployed / 7, 2))
        else:
            return None

    class Meta:
        ordering = ['-season', 'date_deployed', 'station']

    @property
    def has_invasive_spp(self):
        for line in self.lines.all():
            if line.has_invasive_spp:
                return True
        return False

    @property
    def line_count(self):
        return self.lines.count()

    @property
    def species_count(self):
        return SurfaceSpecies.objects.filter(surface__line__sample=self).count()


class SampleSpecies(MetadataFields):
    species = models.ForeignKey(Species, on_delete=models.CASCADE, related_name="sample_spp")
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name="sample_spp")
    observation_date = models.DateTimeField(verbose_name=_("observation date"))
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (('species', 'sample'),)
        verbose_name_plural = _("Sample Species")


class SampleNote(MetadataFields):
    sample = models.ForeignKey(Sample, related_name='notes', on_delete=models.CASCADE, editable=False)
    note = models.TextField()

    date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return str(self.id)

    def get_absolute_url(self):
        return reverse('grais:sample_detail', kwargs={'pk': self.sample.id, })

    class Meta:
        ordering = ["-date"]


class Line(MetadataFields, LatLongFields):
    sample = models.ForeignKey(Sample, related_name='lines', on_delete=models.CASCADE, editable=False)
    collector = models.CharField(max_length=56, blank=True, null=True)
    is_lost = models.BooleanField(default=False, choices=YES_NO_CHOICES, verbose_name="Was the line lost?")
    notes = models.TextField(blank=True, null=True)
    species = models.ManyToManyField(Species, through='LineSpecies')
    last_modified_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        # if the line was lost, set all surfaces to be lost as well
        if self.surfaces.count() > 0:
            if self.is_lost:
                for s in self.surfaces.all():
                    s.is_lost = True
                    s.save()
        if not self.is_lost and self.surfaces.count() > 0:
            lost_list = [surface.is_lost for surface in self.surfaces.all()]
            if not False in lost_list:
                self.is_lost = True

        super().save(*args, **kwargs)

    def __str__(self):
        if self.collector:
            my_str = f'Collector tag #{self.collector}'
        else:
            my_str = f"Line ID #{self.id} (no collector tag)"
        return my_str

    def get_absolute_url(self):
        return reverse('grais:line_detail', kwargs={'pk': self.id})

    @property
    def surface_count(self):
        return self.surfaces.count()

    @property
    def surface_species_count(self):
        return SurfaceSpecies.objects.filter(surface__line=self).count()

    @property
    def has_invasive_spp(self):
        return SurfaceSpecies.objects.filter(surface__line=self, species__invasive=True).exists()

    @property
    def species_list(self):
        if Species.objects.filter(surface_spp__surface__line=self).exists():
            return mark_safe(listrify(Species.objects.filter(surface_spp__surface__line=self).distinct(), "<br>"))
        return "n/a"


def img_file_name(instance, filename):
    img_name = 'grais/sample_{}/{}'.format(instance.line.sample.id, filename)
    return img_name


class LineSpecies(MetadataFields):
    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name="line_spp")
    line = models.ForeignKey(Line, on_delete=models.CASCADE, related_name="line_spp")
    observation_date = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (('species', 'line'),)
        verbose_name_plural = _("Line Species")


class Surface(MetadataFields):
    # Choices for surface_type
    SURFACE_TYPE_CHOICES = (
        ('pe', 'Petri dish'),
        ('pl', 'Plate'),
    )

    line = models.ForeignKey(Line, related_name='surfaces', on_delete=models.CASCADE, editable=False)
    surface_type = models.CharField(max_length=2, choices=SURFACE_TYPE_CHOICES)
    label = models.CharField(max_length=255)
    image = models.ImageField(blank=True, null=True, upload_to=img_file_name)
    is_lost = models.BooleanField(default=False, choices=YES_NO_CHOICES, verbose_name="Was the surface lost?")
    is_damaged = models.BooleanField(default=False, choices=YES_NO_CHOICES, verbose_name="Was the surface damaged?")
    notes = models.TextField(blank=True, null=True)
    species = models.ManyToManyField(Species, through='SurfaceSpecies')
    last_modified_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False)
    old_plateheader_id = models.IntegerField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse('grais:surface_detail', kwargs={
            'pk': self.id
        })

    @property
    def display(self):
        return f"{self.label}" if self.label else f"Surface {self.id} (missing label)"

    def __str__(self):
        return self.display

    class Meta:
        ordering = ['line', 'surface_type', 'label']

    @property
    def has_invasive_spp(self):
        return self.species.filter(invasive=True).exists()

    @property
    def species_count(self):
        return self.species.count()

    @property
    def species_list(self):
        return mark_safe(listrify(self.species.all(), "<br>"))

    @property
    def total_coverage(self):
        return self.surface_spp.all().aggregate(dsum=Sum("percent_coverage"))["dsum"] if self.surface_spp.exists() else 0

    @property
    def total_coverage_display(self):
        return percentage(self.total_coverage)

    @property
    def thumbnail(self):
        if self.image:
            return mark_safe(f'<img src="{self.image.url}" alt="Image not found..." width="150 em">')


class SurfaceSpecies(MetadataFields):
    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name="surface_spp")
    surface = models.ForeignKey(Surface, on_delete=models.CASCADE, related_name="surface_spp")
    percent_coverage = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    notes = models.TextField(blank=True, null=True)
    last_modified_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False)

    class Meta:
        unique_together = (('species', 'surface'),)
        verbose_name_plural = _("Surface Species")

    def get_absolute_url(self):
        return reverse('grais:surface_spp_detail_pop', kwargs={
            'pk': self.id,
        })

    @property
    def coverage_display(self):
        return percentage(self.percent_coverage)


class Probe(models.Model):
    probe_name = models.CharField(max_length=255)
    last_modified_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False)

    def __str__(self):
        return self.probe_name


class ProbeMeasurement(MetadataFields):
    TIMEZONE_CHOICES = (
        ('AST', 'AST'),
        ('ADT', 'ADT'),
        ('UTC', 'UTC'),
    )
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name="probe_data", editable=False)
    probe = models.ForeignKey(Probe, on_delete=models.DO_NOTHING, verbose_name="Probe name")
    time_date = models.DateTimeField(blank=True, null=True, verbose_name="Date / Time (yyyy-mm-dd hh:mm)")
    timezone = models.CharField(max_length=5, choices=TIMEZONE_CHOICES, blank=True, null=True, default="ADT")
    probe_depth = models.FloatField(blank=True, null=True, verbose_name="Probe depth (m)")
    cloud_cover = models.IntegerField(blank=True, null=True, verbose_name="cloud cover (%)", validators=[MinValueValidator(0), MaxValueValidator(100)])
    weather_notes = models.CharField(max_length=1000, blank=True, null=True)
    temp_c = models.FloatField(blank=True, null=True, verbose_name="Temp (°C)")
    sal_ppt = models.FloatField(blank=True, null=True, verbose_name="Salinity (ppt)")
    o2_percent = models.FloatField(blank=True, null=True, verbose_name="Dissolved oxygen (%)")
    o2_mgl = models.FloatField(blank=True, null=True, verbose_name="Dissolved oxygen (mg/l)")
    sp_cond_ms = models.FloatField(blank=True, null=True, verbose_name="Specific conductance (µS)")
    spc_ms = models.FloatField(blank=True, null=True, verbose_name="Conductivity (µS)")
    ph = models.FloatField(blank=True, null=True, verbose_name=" pH")
    turbidity = models.FloatField(blank=True, null=True)

    @property
    def dt(self):
        return f"{self.time_date.strftime('%Y-%m-%d %H:%M')} ({self.timezone})"

    def __str__(self):
        return "Probe measurement {}".format(self.id)


class IncidentalReport(MetadataFields, LatLongFields):
    # Choices for report_source
    REPORT_SOURCE_CHOICES = (
        (1, 'Gulf AIS Hotline'),
        (2, 'Gulf Invaders E-mail'),
        (3, 'Personal E-mail'),
    )

    # Choices for language
    LANGUAGE_CHOICES = (
        (1, 'English'),
        (2, 'French'),
    )

    # Choices for observation_type
    OBSERVATION_TYPE_CHOICES = (
        (1, 'Single observation'),
        (2, 'Ongoing presence'),
    )

    # Choices for requestor
    REQUESTOR_TYPE_CHOICES = (
        (1, "Public"),
        (2, "Academia"),
        (3, "Private sector"),
        (4, "Provincial government"),
        (5, "Federal government"),
    )

    # basic details
    species = models.ManyToManyField(Species, verbose_name="Concerning which species", through='IncidentalReportSpecies')
    report_date = models.DateTimeField(default=timezone.now)
    language_of_report = models.IntegerField(choices=LANGUAGE_CHOICES)
    requestor_name = models.CharField(max_length=150)
    requestor_type = models.IntegerField(choices=REQUESTOR_TYPE_CHOICES, blank=True, null=True)
    phone1 = models.CharField(max_length=50, null=True, blank=True, verbose_name="contact phone (primary)")
    phone2 = models.CharField(max_length=50, null=True, blank=True, verbose_name="contact phone (secondary)")
    email = models.EmailField(null=True, blank=True, verbose_name=_("contact email address"))
    report_source = models.IntegerField(choices=REPORT_SOURCE_CHOICES)
    species_confirmation = models.IntegerField(blank=True, null=True, choices=NULL_YES_NO_CHOICES, verbose_name=_("Was there a species confirmation?"))
    gulf_ais_confirmed = models.IntegerField(blank=True, null=True, choices=NULL_YES_NO_CHOICES, verbose_name=_("Confirmed by Gulf AIS team?"))
    seeking_general_info_ais = models.IntegerField(blank=True, null=True, choices=NULL_YES_NO_CHOICES, verbose_name=_("Seeking general information about AIS?"))
    seeking_general_info_non_ais = models.IntegerField(blank=True, null=True, choices=NULL_YES_NO_CHOICES,
                                                       verbose_name=_("Seeking general information about non-AIS?"))
    management_related = models.IntegerField(blank=True, null=True, choices=NULL_YES_NO_CHOICES, verbose_name=_("Management related?"))
    dfo_it_related = models.IntegerField(blank=True, null=True, choices=NULL_YES_NO_CHOICES, verbose_name=_("DFO IT related?"))
    incorrect_region = models.IntegerField(blank=True, null=True, choices=NULL_YES_NO_CHOICES, verbose_name=_("Incorrect region?"))

    # sighting details
    call_answered_by = models.CharField(max_length=150, null=True, blank=True)
    call_returned_by = models.CharField(max_length=150, null=True, blank=True)
    location_description = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("description of location"))
    latitude = models.FloatField(blank=True, null=True)  # adding here to force order
    longitude = models.FloatField(blank=True, null=True)  # adding here to force order
    specimens_retained = models.IntegerField(blank=True, null=True, choices=NULL_YES_NO_CHOICES, verbose_name=_("were specimens retained?"))
    sighting_description = models.TextField(null=True, blank=True, verbose_name=_("description of sighting"))
    date_of_occurrence = models.DateTimeField()
    identified_by = models.CharField(max_length=150, null=True, blank=True, verbose_name=_("name of identifier"))
    observation_type = models.IntegerField(choices=OBSERVATION_TYPE_CHOICES, verbose_name=_("type of observation"))
    notes = models.TextField(null=True, blank=True)
    season = models.IntegerField(editable=False, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.season = self.report_date.year
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("grais:ir_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return "Incidental Report #{}".format(self.id)

    class Meta:
        ordering = ["-report_date"]

    @property
    def requestor(self):
        mystr = self.requestor_name
        if self.requestor_type:
            mystr += f' ({self.get_requestor_type_display()})'
        return mystr

    @property
    def requestor_information(self):
        mystr = f'<u>Name</u> &rarr; {self.requestor_name}'
        if self.requestor_type:
            mystr += f' ({self.get_requestor_type_display()})'
        if self.phone1:
            mystr += f'<br><u>Phone (primary)</u> &rarr; {self.phone1}'
        if self.phone2:
            mystr += f'<br><u>Phone (secondary)</u> &rarr; {self.phone2}'
        if self.email:
            mystr += f'<br><u>Email</u> &rarr; {self.email}'
        return mark_safe(mystr)

    @property
    def followup_count(self):
        return self.followups.count()

    @property
    def species_list(self):
        return mark_safe(listrify(self.species.all(), "<br>"))


class IncidentalReportSpecies(MetadataFields):
    incidental_report = models.ForeignKey(IncidentalReport, related_name='ir_species', on_delete=models.CASCADE)
    species = models.ForeignKey(Species, related_name='ir_species', on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.species)

    class Meta:
        ordering = ["incidental_report", "species"]


class FollowUp(MetadataFields):
    incidental_report = models.ForeignKey(IncidentalReport, related_name='followups', on_delete=models.CASCADE, editable=False)
    date = models.DateTimeField(default=timezone.now, verbose_name=_("date of follow-up"))
    author = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True)
    note = models.TextField()

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ["-date"]


#########  GREEN CRAB ##########

class Estuary(MetadataFields):
    name = models.CharField(max_length=255, blank=True, null=True)
    province = models.ForeignKey(shared_models.Province, on_delete=models.DO_NOTHING, related_name='estuaries', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.province.abbrev_eng})"

    class Meta:
        ordering = ['name', ]


class Site(LatLongFields, MetadataFields):
    estuary = models.ForeignKey(Estuary, on_delete=models.DO_NOTHING, related_name='sites', blank=True, null=True)
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{} - {} ({})".format(self.code, self.name, self.estuary.name)

    class Meta:
        ordering = ['code', ]


class GCSample(MetadataFields):
    SEDIMENT_CHOICES = (
        (1, 'Sand'),
        (2, 'Mud'),
        (3, 'Sand / Mud'),
    )

    site = models.ForeignKey(Site, related_name='samples', on_delete=models.DO_NOTHING)
    traps_set = models.DateTimeField(verbose_name="Traps set")
    traps_fished = models.DateTimeField(blank=True, null=True, verbose_name="Traps fished")
    samplers = models.ManyToManyField(Sampler)
    eelgrass_assessed = models.IntegerField(blank=True, null=True, choices=NULL_YES_NO_CHOICES, verbose_name="was eelgrass assessed?")
    eelgrass_percent_coverage = models.IntegerField(blank=True, null=True, verbose_name="eelgrass coverage (%)",
                                                    validators=[MinValueValidator(0), MaxValueValidator(100)])
    vegetation_species = models.ManyToManyField(Species, blank=True, limit_choices_to=Q(
        id__in=[5, 6, 46, 131, 132, 133, ]))  # epi alg, ulva, green alg, brown alg, eelg, algae
    sediment = models.IntegerField(null=True, blank=True, choices=SEDIMENT_CHOICES)

    season = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    last_modified = models.DateTimeField(blank=True, null=True, editable=False)
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False)

    # dropdown for spp [epi alg, ulva, green alg, brown alg, eelg, algae]
    # sediment

    def save(self, *args, **kwargs):
        self.season = self.traps_set.year
        self.last_modified = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return "Sample {} - {}".format(self.id, self.site)

    class Meta:
        ordering = ['-season', 'traps_set', 'site']

    @property
    def trap_count(self):
        return self.traps.count()

    @property
    def bycatch_count(self):
        return Catch.objects.filter(species__green_crab_monitoring=False, trap__sample=self).count()

    @property
    def invasive_crabs_count(self):
        return Catch.objects.filter(species__invasive=True, trap__sample=self).count()

    @property
    def noninvasive_crabs_count(self):
        return Catch.objects.filter(species__green_crab_monitoring=True, species__invasive=False, trap__sample=self).count()


class WeatherConditions(UnilingualSimpleLookup):
    name = models.CharField(max_length=50)

    def __str__(self):
        return "{}".format(self.name)


class GCProbeMeasurement(MetadataFields):
    # choice for tide_state
    TIDE_STATE_CHOICES = (
        ('l', "High"),
        ('m', "Mid"),
        ('h', "Low"),
    )

    # choice for tide_direction
    TIDE_DIR_CHOICES = (
        ('in', "Incoming"),
        ('out', "Outgoing"),
    )

    # Choices for timezone
    TIMEZONE_CHOICES = (
        ('AST', 'AST'),
        ('ADT', 'ADT'),
        ('UTC', 'UTC'),
    )

    sample = models.ForeignKey(GCSample, on_delete=models.DO_NOTHING, related_name="probe_data", editable=False)
    probe = models.ForeignKey(Probe, on_delete=models.DO_NOTHING)
    time_date = models.DateTimeField(blank=False, null=True, verbose_name="date / Time (yyyy-mm-dd hh:mm:ss)")
    timezone = models.CharField(max_length=5, choices=TIMEZONE_CHOICES, blank=True, null=True, default="ADT")
    temp_c = models.FloatField(blank=True, null=True, verbose_name="temperature (°C)")
    sal = models.FloatField(blank=True, null=True, verbose_name="salinity")
    o2_percent = models.FloatField(blank=True, null=True, verbose_name="Dissolved oxygen (%)")
    o2_mgl = models.FloatField(blank=True, null=True, verbose_name="Dissolved oxygen (mg/L)")
    sp_cond_ms = models.FloatField(blank=True, null=True, verbose_name="Specific conductance (µS)")
    cond_ms = models.FloatField(blank=True, null=True, verbose_name="Conductivity (µS)")
    tide_state = models.CharField(max_length=5, choices=TIDE_STATE_CHOICES, blank=True, null=True)
    tide_direction = models.CharField(max_length=5, choices=TIDE_DIR_CHOICES, blank=True, null=True)
    cloud_cover = models.IntegerField(blank=True, null=True, verbose_name="cloud cover (%)",
                                      validators=[MinValueValidator(0), MaxValueValidator(100)])
    weather_conditions = models.ManyToManyField(WeatherConditions, verbose_name="weather conditions", blank=True)

    # notes = models.TextField(blank=True, null=True)  # this field should be delete once all data has been entered

    @property
    def tide_description(self):
        my_str = ""
        if self.tide_state:
            my_str += self.get_tide_state_display()
        if self.tide_direction:
            if len(my_str) > 0:
                my_str += " / "
            my_str += self.get_tide_direction_display()
        return my_str

    @property
    def dt(self):
        return f"{self.time_date.strftime('%Y-%m-%d %H:%M')} ({self.timezone})"

    def __str__(self):
        return "Probe measurement {}".format(self.id)


class Bait(UnilingualSimpleLookup):
    pass


class Trap(MetadataFields, LatLongFields):
    # Choices for trap_type
    TRAP_TYPE_CHOICES = (
        (1, 'Fukui'),
        (2, 'Minnow'),
    )
    sample = models.ForeignKey(GCSample, related_name='traps', on_delete=models.DO_NOTHING, editable=False)
    trap_number = models.IntegerField()
    trap_type = models.IntegerField(default=1, choices=TRAP_TYPE_CHOICES)
    bait_type = models.ForeignKey(Bait, related_name='traps', on_delete=models.DO_NOTHING)
    depth_at_set_m = models.FloatField(blank=True, null=True, verbose_name="depth at set (m)")
    gps_waypoint = models.IntegerField(blank=True, null=True, verbose_name="GPS waypoint")
    notes = models.TextField(blank=True, null=True)
    total_green_crab_wt_kg = models.FloatField(blank=True, null=True, verbose_name="Total weight of green crabs (kg)")

    def __str__(self):
        return "Trap #{}".format(self.trap_number)

    class Meta:
        ordering = ['sample', 'trap_number']

    @property
    def bycatch_count(self):
        return self.get_bycatch().count()

    @property
    def invasive_crabs_count(self):
        return self.get_invasive_crabs().count()

    @property
    def noninvasive_crabs_count(self):
        return self.get_noninvasive_crabs().count()

    @property
    def crab_count(self):
        return self.get_crabs().count()

    def get_bycatch(self):
        return self.catch_spp.filter(species__green_crab_monitoring=False)

    def get_crabs(self):
        return self.catch_spp.filter(Q(species__green_crab_monitoring=True))

    def get_invasive_crabs(self):
        return self.catch_spp.filter(species__invasive=True)

    def get_noninvasive_crabs(self):
        return self.catch_spp.filter(species__green_crab_monitoring=True, species__invasive=False)


class Catch(MetadataFields):
    # Choices for sex
    SEX_CHOICES = (
        (1, 'Male'),
        (2, 'Female'),
        (9, 'Unknown'),
    )
    species = models.ForeignKey(Species, on_delete=models.DO_NOTHING, related_name="catch_spp")
    trap = models.ForeignKey(Trap, on_delete=models.DO_NOTHING, related_name="catch_spp")
    width = models.FloatField(blank=True, null=True)
    sex = models.IntegerField(blank=True, null=True, choices=SEX_CHOICES)
    carapace_color = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(4)])
    abdomen_color = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(4)])
    egg_color = models.CharField(max_length=25, blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    last_modified_by = models.ForeignKey(auth.models.User, on_delete=models.DO_NOTHING, blank=True, null=True, editable=False)

    # class Meta:
    #     unique_together = (('species', 'trap'),)

    def __str__(self):
        return "{}".format(self.species)

    class Meta:
        ordering = ['trap', 'species', 'id']

    @property
    def is_bycatch(self):
        return not self.species.green_crab_monitoring

    @property
    def is_invasive_crab(self):
        return self.species.green_crab_monitoring == True and self.species.invasive == True

    @property
    def is_noninvasive_crab(self):
        return self.species.green_crab_monitoring == True and self.species.invasive == False
