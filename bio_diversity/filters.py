import django
import django_filters
from django.utils.translation import gettext as _

from . import models
import shared_models.models as shared_models


class AnidcFilter(django_filters.FilterSet):

    class Meta:
        model = models.AnimalDetCode
        fields = ["name", "nom", "created_by", "created_date", ]


class AdscFilter(django_filters.FilterSet):

    class Meta:
        model = models.AniDetSubjCode
        fields = ["name", "nom", "created_by", "created_date", ]


class CntFilter(django_filters.FilterSet):

    class Meta:
        model = models.Count
        fields = ["loc_id", "contx_id", "spec_id", "created_by", "created_date", ]


class CntcFilter(django_filters.FilterSet):

    class Meta:
        model = models.CountCode
        fields = ["name", "nom", "created_by", "created_date", ]


class CntdFilter(django_filters.FilterSet):

    class Meta:
        model = models.CountDet
        fields = ["cnt_id", "anidc_id", "qual_id", "created_by", "created_date", ]


class CollFilter(django_filters.FilterSet):

    class Meta:
        model = models.Collection
        fields = ["name", "nom", "created_by", "created_date", ]


class ContdcFilter(django_filters.FilterSet):

    class Meta:
        model = models.ContainerDetCode
        fields = ["name", "nom", "min_val", "max_val", "created_by", "created_date", ]


class ContxFilter(django_filters.FilterSet):

    class Meta:
        model = models.ContainerXRef
        fields = ["evnt_id", "created_by", "created_date", ]


class CdscFilter(django_filters.FilterSet):

    class Meta:
        model = models.ContDetSubjCode
        fields = ["name", "nom",  "created_by", "created_date", ]


class CupFilter(django_filters.FilterSet):

    class Meta:
        model = models.Cup
        fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class CupdFilter(django_filters.FilterSet):

    class Meta:
        model = models.CupDet
        fields = ["cup_id", "contdc_id", "cdsc_id", "start_date", "end_date", "created_by", "created_date", ]


class DrawFilter(django_filters.FilterSet):

    class Meta:
        model = models.Drawer
        fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class EnvFilter(django_filters.FilterSet):

    class Meta:
        model = models.EnvCondition
        fields = ["contx_id", "loc_id", "inst_id", "envc_id", "created_by", "created_date", ]


class EnvcFilter(django_filters.FilterSet):

    class Meta:
        model = models.EnvCode
        fields = ["name", "nom", "created_by", "created_date", ]


class EnvscFilter(django_filters.FilterSet):

    class Meta:
        model = models.EnvSubjCode
        fields = ["name", "nom", "envc_id",  "created_by", "created_date", ]


class EnvtFilter(django_filters.FilterSet):

    class Meta:
        model = models.EnvTreatment
        fields = ["contx_id", "envtc_id", "lot_num",  "created_by", "created_date", ]


class EnvtcFilter(django_filters.FilterSet):

    class Meta:
        model = models.EnvTreatCode
        fields = ["name", "nom", "rec_dose", "manufacturer", "created_by", "created_date", ]


class EvntFilter(django_filters.FilterSet):

    class Meta:
        model = models.Event
        fields = ["facic_id", "evntc_id", "perc_id", "prog_id", "team_id", "created_by", "created_date", ]


class EvntcFilter(django_filters.FilterSet):

    class Meta:
        model = models.EventCode
        fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class FacicFilter(django_filters.FilterSet):

    class Meta:
        model = models.FacilityCode
        fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class FecuFilter(django_filters.FilterSet):

    class Meta:
        model = models.Fecundity
        fields = ["stok_id", "coll_id", "alpha", "beta", "created_by", "created_date", ]


class FeedFilter(django_filters.FilterSet):

    class Meta:
        model = models.Feeding
        fields = ["contx_id", "feedm_id", "feedc_id", "created_by", "created_date", ]


class FeedcFilter(django_filters.FilterSet):

    class Meta:
        model = models.FeedCode
        fields = ["name", "nom", "manufacturer", "description_en", "description_fr", "created_by", "created_date", ]


class FeedmFilter(django_filters.FilterSet):

    class Meta:
        model = models.FeedMethod
        fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class GrpFilter(django_filters.FilterSet):

    class Meta:
        model = models.Group
        fields = ["spec_id", "stok_id", "created_by", "created_date", ]


class HeatFilter(django_filters.FilterSet):

    class Meta:
        model = models.HeathUnit
        fields = ["name", "nom", "description_en", "description_fr", "manufacturer", "serial_number", "inservice_date",
                  "created_by", "created_date", ]


class HeatdFilter(django_filters.FilterSet):

    class Meta:
        model = models.HeathUnitDet
        fields = ["heat_id", "contdc_id", "cdsc_id", "start_date", "end_date", "created_by", "created_date", ]


class IndvFilter(django_filters.FilterSet):

    class Meta:
        model = models.Individual
        fields = ["ufid", "spec_id", "stok_id", "created_by", "created_date", ]


class IndvtFilter(django_filters.FilterSet):

    class Meta:
        model = models.IndTreatment
        fields = ["indvtc_id", "lot_num", "created_by", "created_date", ]


class IndvtcFilter(django_filters.FilterSet):

    class Meta:
        model = models.IndTreatCode
        fields = ["name", "nom", "rec_dose", "manufacturer", "created_by", "created_date", ]


class InstFilter(django_filters.FilterSet):

    class Meta:
        model = models.Instrument
        fields = ["instc", "serial_number", "created_by", "created_date", ]


class InstcFilter(django_filters.FilterSet):

    class Meta:
        model = models.InstrumentCode
        fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class InstdFilter(django_filters.FilterSet):

    class Meta:
        model = models.InstrumentDet
        fields = ["inst", "instdc", "valid", "created_by", "created_date", ]


class InstdcFilter(django_filters.FilterSet):

    class Meta:
        model = models.InstDetCode
        fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class LocFilter(django_filters.FilterSet):

    class Meta:
        model = models.Location
        fields = ["evnt_id", "rive_id", "trib_id", "relc_id", "loc_date", "created_by", "created_date", ]


class LoccFilter(django_filters.FilterSet):

    class Meta:
        model = models.LocCode
        fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class OrgaFilter(django_filters.FilterSet):

    class Meta:
        model = models.Organization
        fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class PairFilter(django_filters.FilterSet):

    class Meta:
        model = models.Pairing
        fields = ["indv_id", "created_by", "created_date", ]


class PercFilter(django_filters.FilterSet):

    class Meta:
        model = models.PersonnelCode
        fields = ["perc_first_name", "perc_last_name", "perc_valid", "created_by", "created_date", ]


class PrioFilter(django_filters.FilterSet):

    class Meta:
        model = models.PriorityCode
        fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class ProgFilter(django_filters.FilterSet):

    class Meta:
        model = models.Program
        fields = ["prog_name", "proga_id", "orga_id",  "created_by", "created_date", ]


class ProgaFilter(django_filters.FilterSet):

    class Meta:
        model = models.ProgAuthority
        fields = ["proga_last_name", "proga_first_name", "created_by", "created_date", ]


class ProtFilter(django_filters.FilterSet):

    class Meta:
        model = models.Protocol
        fields = ["prog_id", "protc_id", "created_by", "created_date", ]


class ProtcFilter(django_filters.FilterSet):

    class Meta:
        model = models.ProtoCode
        fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class ProtfFilter(django_filters.FilterSet):

    class Meta:
        model = models.Protofile
        fields = ["prot_id", "created_by", "created_date", ]


class QualFilter(django_filters.FilterSet):

    class Meta:
        model = models.QualCode
        fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class RelcFilter(django_filters.FilterSet):

    class Meta:
        model = models.ReleaseSiteCode
        fields = ["rive_id", "trib_id", "name", "nom", "created_by", "created_date", ]


class RiveFilter(django_filters.FilterSet):

    class Meta:
        model = models.RiverCode
        fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class RoleFilter(django_filters.FilterSet):

    class Meta:
        model = models.RoleCode
        fields = ["name", "nom", "created_by", "created_date", ]


class SampFilter(django_filters.FilterSet):

    class Meta:
        model = models.Sample
        fields = ["loc_id", "samp_num",  "spec_id", "created_by", "created_date", ]


class SampcFilter(django_filters.FilterSet):

    class Meta:
        model = models.SampleCode
        fields = ["name", "nom", "created_by", "created_date", ]


class SampdFilter(django_filters.FilterSet):

    class Meta:
        model = models.SampleDet
        fields = ["samp_id", "anidc_id", "created_by", "created_date", ]


class SpwndcFilter(django_filters.FilterSet):

    class Meta:
        model = models.SpawnDetCode
        fields = ["name", "nom", "created_by", "created_date", ]


class SpwnscFilter(django_filters.FilterSet):

    class Meta:
        model = models.SpawnDetSubjCode
        fields = ["name", "nom", "created_by", "created_date", ]


class SpecFilter(django_filters.FilterSet):

    class Meta:
        model = models.SpeciesCode
        fields = ["name", "species", "com_name", "created_by", "created_date", ]


class StokFilter(django_filters.FilterSet):

    class Meta:
        model = models.StockCode
        fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class SubrFilter(django_filters.FilterSet):

    class Meta:
        model = models.SubRiverCode
        fields = ["name", "nom", "rive_id", "trib_id", "description_en", "description_fr", "created_by",
                  "created_date", ]


class TankFilter(django_filters.FilterSet):

    class Meta:
        model = models.Tank
        fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class TankdFilter(django_filters.FilterSet):

    class Meta:
        model = models.TankDet
        fields = ["tank_id", "contdc_id", "cdsc_id", "start_date", "end_date", "created_by", "created_date", ]


class TeamFilter(django_filters.FilterSet):

    class Meta:
        model = models.Team
        fields = ["perc_id", "role_id", "created_by", "created_date", ]


class TrayFilter(django_filters.FilterSet):

    class Meta:
        model = models.Tray
        fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class TraydFilter(django_filters.FilterSet):

    class Meta:
        model = models.TrayDet
        fields = ["tray_id", "contdc_id", "cdsc_id", "start_date", "end_date", "created_by", "created_date", ]


class TribFilter(django_filters.FilterSet):

    class Meta:
        model = models.Tributary
        fields = ["name", "nom", "rive_id", "description_en", "description_fr", "created_by", "created_date", ]


class TrofFilter(django_filters.FilterSet):

    class Meta:
        model = models.Trough
        fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class TrofdFilter(django_filters.FilterSet):

    class Meta:
        model = models.TroughDet
        fields = ["trof_id", "contdc_id", "cdsc_id", "start_date", "end_date", "created_by", "created_date", ]


class UnitFilter(django_filters.FilterSet):

    class Meta:
        model = models.UnitCode
        fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]
