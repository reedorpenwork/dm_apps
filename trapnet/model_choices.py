from django.utils.translation import gettext_lazy as _

wind_speed_choices = (
    (1, _("no wind")),
    (2, _("calm / slight wind")),
    (3, _("light wind")),
    (4, _("moderate wind")),
    (5, _("heavy wind")),
    (6, _("variable")),
)

wind_direction_choices = (
    (1, _("north")),
    (2, _("northeast")),
    (3, _("east")),
    (4, _("southeast")),
    (5, _("south")),
    (6, _("southwest")),
    (7, _("west")),
    (8, _("northwest")),
)

precipitation_category_choices = (
    (1, _("no precipitation")),
    (2, _("mist")),
    (3, _("light rain")),
    (4, _("moderate rain")),
    (5, _("heavy rain")),
    (6, _("intermittent")),
    (7, _("flurries")),
)

operating_condition_choices = (
    (1, _("fully operational")),
    (2, _("partially operational")),
    (3, _("not operational")),
)

status_choices = (
    (1, _("unreviewed")),
    (2, _("reviewed")),
)

sample_type_choices = (
    (1, _("Rotary Screw Trap")),
    (2, _("Electrofishing")),
    (3, _("Trapnet")),
)

site_type_choices = (
    (1, _("Open")),
    (2, _("Closed")),
)

seine_type_choices = (
    (1, _("1 man seine (1m wide X 1m high)")),
    (2, _("2 man lip seine (3m wide X 1m high)")),
)

pulse_type_choices = (
    (1, _("Standard pulse ")),
    (2, _("Direct current")),
    (3, _("Burst of pulses")),
)

adipose_condition_choices = (
    (None, _("Not checked")),
    (0, _("Absent")),
    (1, _("Present")),
)

didymo_choices = (
    (None, _("No data")),
    (0, _("Absent")),
    (1, _("Present")),
)

sea_lice_choices = (
    (None, "None"),
    (1, "< 5"),
    (2, "5-15"),
    (3, "15-50"),
    (4, "> 50"),
)

age_type_choices = (
    (1, _("scale")),
    (2, _("length-frequency, manual")),
    (3, _("length-frequency, auto")),
)

length_type_choices = (
    (1, "fork"),
    (2, "total"),
)
