import datetime
import math

import pytz
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import JsonResponse
from django.utils import timezone
from decimal import Decimal
from bio_diversity import models


def bio_diverisity_authorized(user):
    # return user.is_user and user.groups.filter(name='bio_diversity_user').exists()
    return user.groups.filter(name='bio_diversity_user').exists() or bio_diverisity_admin(user)


def bio_diverisity_admin(user):
    # return user.is_authenticated and user.groups.filter(name='bio_diversity_admin').exists()
    return user.groups.filter(name='bio_diversity_admin').exists()


def get_comment_keywords_dict():
    my_dict = {}
    for obj in models.CommentKeywords.objects.all():
        my_dict[obj.keyword] = obj.adsc_id
    return my_dict


def get_help_text_dict(model=None, title=''):
    my_dict = {}
    if not model:
        for obj in models.HelpText.objects.all():
            my_dict[obj.field_name] = str(obj)
    else:
        # If a model is supplied get the fields specific to that model
        for obj in models.HelpText.objects.filter(model=str(model.__name__)):
            my_dict[obj.field_name] = str(obj)

    return my_dict


def year_coll_splitter(full_str):
    coll = full_str.lstrip(' 0123456789')
    year = int(full_str[:len(full_str) - len(coll)])
    return year, coll.strip()


def val_unit_splitter(full_str):
    unit_str = full_str.lstrip(' 0123456789.')
    val = float(full_str[:len(full_str) - len(unit_str)])
    return val, unit_str.strip()


def parse_concentration(concentration_str):
    if "%" in concentration_str:
        return Decimal(float(concentration_str.rstrip("%"))/100)
    elif ":" in concentration_str:
        concentration_str = concentration_str.replace(" ", "")
        concentration_str = concentration_str.replace("1:", "", 1)
        return Decimal(1.0/float(concentration_str))
    else:
        return None


def get_cont_evnt(contx_tuple):
    # input should be in the form (contx, bool/null)
    contx = contx_tuple[0]
    in_out_dict = {None: "", False: "Origin", True: "Destination"}
    output_list = [contx.evnt_id.evntc_id.__str__(), contx.evnt_id.start_date, in_out_dict[contx_tuple[1]]]
    for cont in [contx.tank_id, contx.cup_id, contx.tray_id, contx.trof_id, contx.draw_id, contx.heat_id]:
        if cont:
            output_list.append("{}".format(cont.__str__()))
            break
    return output_list


def comment_parser(comment_str, anix_indv, det_date):
    coke_dict = get_comment_keywords_dict()
    parser_list = coke_dict.keys()
    mortality = False
    for term in parser_list:
        if term.lower() in comment_str.lower():
            adsc = coke_dict[term]
            if adsc.name == "Mortality":
                mortality = True
            indvd_parsed = models.IndividualDet(anix_id_id=anix_indv.pk,
                                                anidc_id=adsc.anidc_id,
                                                adsc_id=adsc,
                                                qual_id=models.QualCode.objects.filter(name="Good").get(),
                                                detail_date=det_date,
                                                comments=comment_str,
                                                created_by=anix_indv.created_by,
                                                created_date=anix_indv.created_date,
                                                )
            try:
                indvd_parsed.clean()
                indvd_parsed.save()
            except (ValidationError, IntegrityError):
                pass
    if mortality:
        anix_indv.indv_id.indv_valid = False
        anix_indv.indv_id.save()


def create_movement_evnt(origin, destination, cleaned_data, movement_date=None, indv_pk=None, grp_pk=None):
    row_entered = False
    origin = str(origin)
    destination = str(destination)
    new_cleaned_data = cleaned_data.copy()
    if origin == destination:
        row_entered = False
        return row_entered

    if enter_tank_contx(origin, cleaned_data, None):
        row_entered = True

    if enter_tank_contx(destination, cleaned_data, None):
        row_entered = True

    if not origin == "nan" and not destination == "nan":
        movement_evnt = models.Event(evntc_id=models.EventCode.objects.filter(name="Movement").get(),
                                     facic_id=cleaned_data["evnt_id"].facic_id,
                                     perc_id=cleaned_data["evnt_id"].perc_id,
                                     prog_id=cleaned_data["evnt_id"].prog_id,
                                     start_datetime=movement_date,
                                     end_datetime=movement_date,
                                     created_by=new_cleaned_data["created_by"],
                                     created_date=new_cleaned_data["created_date"],
                                     )
        try:
            movement_evnt.clean()
            movement_evnt.save()
            row_entered = True
        except (ValidationError, IntegrityError):
            movement_evnt = models.Event.objects.filter(evntc_id=movement_evnt.evntc_id,
                                                        facic_id=movement_evnt.facic_id,
                                                        prog_id=movement_evnt.prog_id,
                                                        start_datetime=movement_evnt.start_datetime,
                                                        end_datetime=movement_evnt.end_datetime,
                                                        ).get()

        new_cleaned_data["evnt_id"] = movement_evnt
        if indv_pk:
            enter_anix(new_cleaned_data, indv_pk=indv_pk)
        if grp_pk:
            enter_anix(new_cleaned_data, grp_pk=grp_pk)
        if enter_tank_contx(origin, new_cleaned_data, False, indv_pk=indv_pk, grp_pk=grp_pk):
            row_entered = True
        if enter_tank_contx(destination, new_cleaned_data, True, indv_pk=indv_pk, grp_pk=grp_pk):
            row_entered = True

        return row_entered


def enter_anix(cleaned_data, indv_pk=None, contx_pk=None, loc_pk=None, pair_pk=None, grp_pk=None, indvt_pk=None, final_flag=None):
    if any([indv_pk, contx_pk, loc_pk, pair_pk, grp_pk, indvt_pk]):
        anix = models.AniDetailXref(evnt_id_id=cleaned_data["evnt_id"].pk,
                                    indv_id_id=indv_pk,
                                    contx_id_id=contx_pk,
                                    loc_id_id=loc_pk,
                                    pair_id_id=pair_pk,
                                    grp_id_id=grp_pk,
                                    indvt_id_id=indvt_pk,
                                    final_contx_flag=final_flag,
                                    created_by=cleaned_data["created_by"],
                                    created_date=cleaned_data["created_date"],
                                    )
        try:
            anix.clean()
            anix.save()
            return anix
        except ValidationError:
            anix = models.AniDetailXref.objects.filter(evnt_id=anix.evnt_id,
                                                       indv_id=anix.indv_id,
                                                       contx_id=anix.contx_id,
                                                       loc_id=anix.loc_id,
                                                       pair_id=anix.pair_id,
                                                       grp_id=anix.grp_id,
                                                       indvt_id=anix.indvt_id,
                                                       ).get()
            return anix


def enter_anix_contx(tank, cleaned_data):
    if tank:
        contx = models.ContainerXRef(evnt_id=cleaned_data["evnt_id"],
                                     tank_id=tank,
                                     created_by=cleaned_data["created_by"],
                                     created_date=cleaned_data["created_date"],
                                     )
        try:
            contx.clean()
            contx.save()
            return contx
        except ValidationError:
            contx = models.ContainerXRef.objects.filter(evnt_id=contx.evnt_id,
                                                        tank=contx.tank_id,
                                                        ).get()

        anix_contx = enter_anix(cleaned_data, contx_pk=contx.pk)
        return anix_contx


def enter_cnt(cleaned_data, cnt_value, contx_pk=None, loc_pk=None, cnt_code="Number of Fish", est=False):
    cnt = False
    if not math.isnan(cnt_value):
        cnt = models.Count(loc_id_id=loc_pk,
                           contx_id_id=contx_pk,
                           spec_id=models.SpeciesCode.objects.filter(name__iexact="Salmon").get(),
                           cntc_id=models.CountCode.objects.filter(name__iexact=cnt_code).get(),
                           cnt=cnt_value,
                           est=est,
                           created_by=cleaned_data["created_by"],
                           created_date=cleaned_data["created_date"],
                           )
        try:
            cnt.clean()
            cnt.save()
        except ValidationError:
            cnt = models.Count.objects.filter(loc_id=cnt.loc_id, contx_id=cnt.contx_id, cntc_id=cnt.cntc_id).get()
            if cnt_code == "Mortality":
                cnt.cnt += 1
                cnt.save()
    return cnt


def enter_cnt_det(cleaned_data, cnt_pk, det_val, det_code, qual="Good"):
    row_entered = False
    if not math.isnan(det_val):
        cntd = models.CountDet(cnt_id_id=cnt_pk,
                               anidc_id=models.AnimalDetCode.objects.filter(
                                   name__iexact=det_code).get(),
                               det_val=det_val,
                               qual_id=models.QualCode.objects.filter(name=qual).get(),
                               created_by=cleaned_data["created_by"],
                               created_date=cleaned_data["created_date"],
                               )
        try:
            cntd.clean()
            cntd.save()
            row_entered = True
        except ValidationError:
            row_entered = False
    return row_entered


def enter_env(env_value, env_date, cleaned_data, envc_id, envsc_id=None, loc_id=None, contx=None, inst_id=None, env_start=None, avg=False, save=True, qual_id=False):
    row_entered = False
    if isinstance(env_value, float):
        if math.isnan(env_value):
            return False
    if env_start:
        env_datetime = datetime.datetime.combine(env_date, env_start).replace(tzinfo=pytz.UTC)
    else:
        env_datetime = datetime.datetime.combine(env_date, datetime.datetime.min.time()).replace(tzinfo=pytz.UTC)

    if not qual_id:
        qual_id = models.QualCode.objects.filter(name="Good").get()

    if envsc_id:
        env = models.EnvCondition(contx_id=contx,
                                  loc_id=loc_id,
                                  envc_id=envc_id,
                                  envsc_id=envsc_id,
                                  inst_id=inst_id,
                                  env_val=str(env_value),
                                  env_avg=avg,
                                  start_datetime=env_datetime,
                                  qual_id=qual_id,
                                  created_by=cleaned_data["created_by"],
                                  created_date=cleaned_data["created_date"],
                                  )
    else:
        env = models.EnvCondition(contx_id=contx,
                                  loc_id=loc_id,
                                  envc_id=envc_id,
                                  inst_id=inst_id,
                                  env_val=str(env_value),
                                  env_avg=avg,
                                  start_datetime=env_datetime,
                                  qual_id=qual_id,
                                  created_by=cleaned_data["created_by"],
                                  created_date=cleaned_data["created_date"],
                                  )
    if save:
        try:
            env.clean()
            env.save()
            row_entered = True
        except (ValidationError, IntegrityError):
            pass
        return row_entered
    else:
        try:
            env.clean()
            return env
        except (ValidationError, IntegrityError):
            return None


def enter_grpd(anix_pk, cleaned_data, det_date, det_value, anidc_str, adsc_str=None, comments=None):
    row_entered = False
    if isinstance(det_value, float):
        if math.isnan(det_value):
            return False
    if adsc_str:
        grpd = models.GroupDet(anix_id_id=anix_pk,
                               anidc_id=models.AnimalDetCode.objects.filter(name=anidc_str).get(),
                               adsc_id=models.AniDetSubjCode.objects.filter(name=adsc_str).get(),
                               det_val=det_value,
                               detail_date=det_date,
                               qual_id=models.QualCode.objects.filter(name="Good").get(),
                               comments=comments,
                               created_by=cleaned_data["created_by"],
                               created_date=cleaned_data["created_date"],
                               )
    else:
        grpd = models.GroupDet(anix_id_id=anix_pk,
                               anidc_id=models.AnimalDetCode.objects.filter(name=anidc_str).get(),
                               det_val=det_value,
                               detail_date=det_date,
                               qual_id=models.QualCode.objects.filter(name="Good").get(),
                               created_by=cleaned_data["created_by"],
                               created_date=cleaned_data["created_date"],
                               )
    try:
        grpd.clean()
        grpd.save()
        row_entered = True
    except (ValidationError, IntegrityError):
        pass
    return row_entered


def enter_indvd(anix_pk, cleaned_data, det_date, det_value, anidc_str, adsc_str, comments=None):
    row_entered = False
    if isinstance(det_value, float):
        if math.isnan(det_value):
            return False
    if adsc_str:
        indvd = models.IndividualDet(anix_id_id=anix_pk,
                                     anidc_id=models.AnimalDetCode.objects.filter(name=anidc_str).get(),
                                     adsc_id=models.AniDetSubjCode.objects.filter(name=adsc_str).get(),
                                     det_val=det_value,
                                     detail_date=det_date,
                                     qual_id=models.QualCode.objects.filter(name="Good").get(),
                                     comments=comments,
                                     created_by=cleaned_data["created_by"],
                                     created_date=cleaned_data["created_date"],
                                     )
    else:
        indvd = models.IndividualDet(anix_id_id=anix_pk,
                                     anidc_id=models.AnimalDetCode.objects.filter(name=anidc_str).get(),
                                     det_val=det_value,
                                     detail_date=det_date,
                                     qual_id=models.QualCode.objects.filter(name="Good").get(),
                                     created_by=cleaned_data["created_by"],
                                     created_date=cleaned_data["created_date"],
                                     )
    try:
        indvd.clean()
        indvd.save()
        row_entered = True
    except (ValidationError, IntegrityError):
        pass
    return row_entered


def enter_mortality(indv, cleaned_data, mort_date):
    mortality_evnt = models.Event(evntc_id=models.EventCode.objects.filter(name="Mortality").get(),
                                  facic_id=cleaned_data["evnt_id"].facic_id,
                                  prog_id=cleaned_data["evnt_id"].prog_id,
                                  perc_id=cleaned_data["evnt_id"].perc_id,
                                  start_datetime=mort_date,
                                  end_datetime=mort_date,
                                  created_by=cleaned_data["created_by"],
                                  created_date=cleaned_data["created_date"],
                                  )
    try:
        mortality_evnt.clean()
        mortality_evnt.save()
    except (ValidationError, IntegrityError):
        mortality_evnt = models.Event.objects.filter(evntc_id=mortality_evnt.evntc_id,
                                                     facic_id=mortality_evnt.facic_id,
                                                     prog_id=mortality_evnt.prog_id,
                                                     start_datetime=mortality_evnt.start_datetime,
                                                     end_datetime=mortality_evnt.end_datetime,
                                                     ).get()
    new_cleaned_data = cleaned_data.copy()
    new_cleaned_data["evnt_id"] = mortality_evnt
    anix = enter_anix(new_cleaned_data, indv_pk=indv.pk)
    indv.indv_valid = False
    indv.save()
    return mortality_evnt, anix


def enter_spwnd(pair_pk, cleaned_data, det_value, spwndc_str, spwnsc_str, qual_code="Good", comments=None):
    row_entered = False
    if isinstance(det_value, float):
        if math.isnan(det_value):
            return False
    if spwnsc_str:
        spwnd = models.SpawnDet(pair_id_id=pair_pk,
                                anidc_id=models.SpawnDetCode.objects.filter(name=spwndc_str).get(),
                                adsc_id=models.SpawnDetSubjCode.objects.filter(name=spwnsc_str).get(),
                                det_val=det_value,
                                qual_id=models.QualCode.objects.filter(name=qual_code).get(),
                                comments=comments,
                                created_by=cleaned_data["created_by"],
                                created_date=cleaned_data["created_date"],
                                )
    else:
        spwnd = models.SpawnDet(pair_id_id=pair_pk,
                                spwndc_id=models.SpawnDetCode.objects.filter(name=spwndc_str).get(),
                                det_val=det_value,
                                qual_id=models.QualCode.objects.filter(name=qual_code).get(),
                                created_by=cleaned_data["created_by"],
                                created_date=cleaned_data["created_date"],
                                )
        try:
            spwnd.clean()
            spwnd.save()
            row_entered = True
        except ValidationError:
            pass
    return row_entered


def enter_tank_contx(tank_name, cleaned_data, final_flag=None, indv_pk=None, grp_pk=None, return_contx=False):
    row_entered = False
    if not tank_name == "nan":
        contx = models.ContainerXRef(evnt_id_id=cleaned_data["evnt_id"].pk,
                                     tank_id=models.Tank.objects.filter(name=tank_name, facic_id=cleaned_data["facic_id"]).get(),
                                     created_by=cleaned_data["created_by"],
                                     created_date=cleaned_data["created_date"],
                                     )
        try:
            contx.clean()
            contx.save()
            row_entered = True
        except ValidationError:
            contx = models.ContainerXRef.objects.filter(evnt_id=contx.evnt_id,
                                                        tank_id=contx.tank_id).get()
        if indv_pk or grp_pk:
            enter_anix(cleaned_data, indv_pk=indv_pk, grp_pk=grp_pk, contx_pk=contx.pk, final_flag=final_flag)
        if return_contx:
            return contx
        else:
            return row_entered
    else:
        return False


def enter_trof_contx(trof_name, cleaned_data, final_flag=None, indv_pk=None, grp_pk=None, return_contx=False):
    row_entered = False
    if not trof_name == "nan":
        contx = models.ContainerXRef(evnt_id_id=cleaned_data["evnt_id"].pk,
                                     trof_id=models.Trough.objects.filter(name=trof_name, facic_id=cleaned_data["facic_id"]).get(),
                                     created_by=cleaned_data["created_by"],
                                     created_date=cleaned_data["created_date"],
                                     )
        try:
            contx.clean()
            contx.save()
            row_entered = True
        except ValidationError:
            contx = models.ContainerXRef.objects.filter(evnt_id=contx.evnt_id,
                                                        trof_id=contx.trof_id).get()
        if indv_pk or grp_pk:
            enter_anix(cleaned_data, indv_pk=indv_pk, grp_pk=grp_pk, contx_pk=contx.pk, final_flag=final_flag)
        if return_contx:
            return contx
        else:
            return row_entered
    else:
        return False


def ajax_get_fields(request):
    model_name = request.GET.get('model', None)

    # use the model name passed from the web page to find the model in the apps models file
    model = models.__dict__[model_name]

    # use the retrieved model and get the doc string which is a string in the format
    # SomeModelName(id, field1, field2, field3)
    # remove the trailing parentheses, split the string up based on ', ', then drop the first element
    # which is the model name and the id.
    match = str(model.__dict__['__doc__']).replace(")", "").split(", ")[1:]
    fields = list()
    for f in match:
        label = "---"
        attr = getattr(model, f).field
        if hasattr(attr, 'verbose_name'):
            label = attr.verbose_name

        fields.append([f, label])

    data = {
        'fields': fields
    }

    return JsonResponse(data)
