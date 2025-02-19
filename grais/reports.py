import os
import statistics

import unicodecsv as csv
import xlsxwriter as xlsxwriter
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import floatformat
from django.utils import timezone

from dm_apps.utils import Echo
from lib.functions.custom_functions import nz, listrify
from lib.functions.verbose_field_name import verbose_field_name
from lib.templatetags.verbose_names import get_verbose_label, get_field_value
from . import models


def generate_species_sample_spreadsheet(year, species_list=None):
    # figure out the filename
    target_dir = os.path.join(settings.BASE_DIR, 'media', 'grais', 'temp')
    target_file = "temp_data_export_{}.xlsx".format(timezone.now().strftime("%Y-%m-%d"))
    target_file_path = os.path.join(target_dir, target_file)
    target_url = os.path.join(settings.MEDIA_ROOT, 'grais', 'temp', target_file)

    # create workbook and worksheets
    workbook = xlsxwriter.Workbook(target_file_path)

    # create formatting
    header_format = workbook.add_format(
        {'bold': True, 'border': 1, 'border_color': 'black', 'bg_color': '#8C96A0', "align": 'normal',
         "text_wrap": True})
    normal_format = workbook.add_format({"align": 'left', "text_wrap": True})
    # Add a format. Light red fill with dark red text.
    red_format = workbook.add_format({'bg_color': '#FFC7CE',
                                      'font_color': '#9C0006'})

    # Add a format. Green fill with dark green text.
    green_format = workbook.add_format({'bg_color': '#C6EFCE',
                                        'font_color': '#006100'})

    # get a sample instance to create header
    my_sample = models.Sample.objects.first()
    my_species = models.Species.objects.first()

    # define the header
    header = [
        "Species ID",
        verbose_field_name(my_species, 'common_name'),
        verbose_field_name(my_species, 'scientific_name'),
        verbose_field_name(my_species, 'abbrev'),
        verbose_field_name(my_species, 'epibiont_type'),
        verbose_field_name(my_species, 'tsn'),
        verbose_field_name(my_species, 'aphia_id'),
        "Sample ID",
        "Observation platform",
        "Observation year",
        "Observation month",
        "Observation day",
        verbose_field_name(my_sample, 'station'),
        verbose_field_name(my_sample.station, 'province'),
        verbose_field_name(my_sample.station, 'latitude'),
        verbose_field_name(my_sample.station, 'longitude'),
        "observed at station?",
        "observed on line?",
        "observed on collector surface?",
        "% surface coverage - plates (mean)",
        "% surface coverage - petris (mean)",
    ]

    # worksheets #
    ##############
    new_species_list = [models.Species.objects.get(pk=int(s)) for s in species_list.split(",")]
    i = 1
    my_ws = workbook.add_worksheet(name="Samples")
    for species in new_species_list:

        # create the col_max column to store the length of each header
        # should be a maximum column width to 100
        col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header]
        my_ws.write_row(0, 0, header, header_format)

        # get a list of samples for each requested species FROM ALL SOURCES
        samples = models.Sample.objects.all()
        if year and year != "None":
            samples = samples.filter(season=int(year))
        sample_list = [samples.get(pk=s["surface__line__sample"]) for s in
                       models.SurfaceSpecies.objects.filter(species=species, surface__line__sample__in=samples).values("surface__line__sample").distinct()]
        sample_list.extend(
            [models.Sample.objects.get(pk=s["sample"]) for s in
             models.SampleSpecies.objects.filter(species=species, sample__in=samples).values("sample").distinct()]
        )
        sample_list.extend(
            [models.Sample.objects.get(pk=s["line__sample"]) for s in
             models.LineSpecies.objects.filter(species=species, line__sample__in=samples).values("line__sample").distinct()]
        )
        # distill the list
        sample_set = set(sample_list)

        for sample in sample_set:
            if sample.date_retrieved:
                obs_year = sample.date_retrieved.year
                obs_month = sample.date_retrieved.month
                obs_day = sample.date_retrieved.day
            else:
                obs_year = None
                obs_month = None
                obs_day = None

            if models.SampleSpecies.objects.filter(sample=sample, species=species).count() > 0:
                at_station = "yes"
            else:
                at_station = "no"

            if models.LineSpecies.objects.filter(line__sample=sample, species=species).count() > 0:
                on_line = "yes"
            else:
                on_line = "no"

            if models.SurfaceSpecies.objects.filter(surface__line__sample=sample, species=species).count() > 0:
                on_surface = "yes"
            else:
                on_surface = "no"

            # calculate the % coverage
            if on_surface:
                # for each surface, determine the percent coverage and store in list
                coverage_list_pl = []
                coverage_list_pe = []
                for surface in models.Surface.objects.filter(line__sample=sample).all():
                    if surface.surface_type == "pl":
                        try:
                            my_coverage = models.SurfaceSpecies.objects.get(surface=surface, species=species).percent_coverage
                        except:
                            my_coverage = 0
                        coverage_list_pl.append(my_coverage)

                    elif surface.surface_type == "pe":
                        try:
                            my_coverage = models.SurfaceSpecies.objects.get(surface=surface, species=species).percent_coverage
                        except:
                            my_coverage = 0
                        coverage_list_pe.append(my_coverage)
                try:
                    mean_pl_coverage = statistics.mean(coverage_list_pl)
                except statistics.StatisticsError:
                    mean_pl_coverage = 0
                try:
                    mean_pe_coverage = statistics.mean(coverage_list_pe)
                except statistics.StatisticsError:
                    mean_pe_coverage = 0

            data_row = [
                species.id,
                species.common_name,
                species.scientific_name,
                species.abbrev,
                species.get_epibiont_type_display(),
                species.tsn,
                species.aphia_id,
                sample.id,
                'Biofouling Monitoring',
                obs_year,
                obs_month,
                obs_day,
                sample.station.station_name,
                sample.station.province.tabbrev,
                sample.station.latitude,
                sample.station.longitude,
                at_station,
                on_line,
                on_surface,
                mean_pl_coverage,
                mean_pe_coverage,
            ]

            # adjust the width of the columns based on the max string length in each col
            ## replace col_max[j] if str length j is bigger than stored value

            j = 0
            for d in data_row:
                # if new value > stored value... replace stored value
                if len(str(d)) > col_max[j]:
                    if len(str(d)) < 100:
                        col_max[j] = len(str(d))
                    else:
                        col_max[j] = 100
                j += 1

            my_ws.write_row(i, 0, data_row, normal_format)
            i += 1

        for j in range(0, len(col_max)):
            my_ws.set_column(j, j, width=col_max[j] * 1.1)

        # set formatting for last three columns
        my_ws.conditional_format(0, header.index("observed at station?"), i,
                                 header.index("observed on collector surface?"),
                                 {
                                     'type': 'cell',
                                     'criteria': 'equal to',
                                     'value': '"yes"',
                                     'format': green_format,
                                 })
        my_ws.conditional_format(0, header.index("observed at station?"), i,
                                 header.index("observed on collector surface?"),
                                 {
                                     'type': 'cell',
                                     'criteria': 'equal to',
                                     'value': '"no"',
                                     'format': red_format,
                                 })

    workbook.close()
    return target_url


def generate_biofouling_pa_spreadsheet(year=None):
    """Returns a generator for an HTTP Streaming Response"""

    stations = models.Station.objects.all()
    if year:
        years = [year]
    else:
        years = [item["season"] for item in models.Sample.objects.order_by("season").values("season").distinct()]

    header_row = [
        "Year",
        "Station",
        "Province",
        "Latitude",
        "Longitude",
        "B schlosseri",
        "B violaceus",
        "C intestinalis",
        "S clava",
        "C mutica",
        "M membranacea",
        "C maenas",
        "C fragile",
    ]

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    yield writer.writerow(header_row)

    ais_list = [get_object_or_404(models.Species, pk=id) for id in [24, 48, 23, 25, 47, 59, 26, 55]]
    for year in years:
        for station in stations:
            sample_qs = models.Sample.objects.filter(season=year, station=station)

            for sample in sample_qs:
                data_row = [
                    year,
                    station.station_name,
                    station.province.abbrev_eng,
                    station.latitude,
                    station.longitude,
                ]

                for ais in ais_list:
                    # does a sample even exist?
                    # start out optimistic
                    has_been_observed = 0

                    # we will have to search in three places: sample level, line level, collector level
                    if models.SampleSpecies.objects.filter(sample=sample, species=ais).exists():
                        has_been_observed = 1
                    elif models.LineSpecies.objects.filter(line__sample=sample, species=ais).exists():
                        has_been_observed = 1
                    elif models.SurfaceSpecies.objects.filter(surface__line__sample=sample, species=ais).exists():
                        has_been_observed = 1

                    data_row.append(has_been_observed)
                yield writer.writerow(data_row)


def generate_open_data_ver_1_data_dictionary():
    """
    Generates the data dictionary for open data report version 1
    """

    filename = "data_dictionary.csv"

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer = csv.writer(response)
    species_id_list = [48, 24, 47, 23, 55, 59, 25]
    species_qs = models.Species.objects.filter(id__in=species_id_list)

    # write the header
    header = [
        "name__nom",
        "description_en",
        "description_fr",
    ]
    writer.writerow(header)

    field_names = [
        'Sampling year',
        'Station code',
        'Station name',
        'Date in',
        'Date out',
        'Weeks',
        'Station Description',
        'Collector Latitude',
        'Collector Longitude',
        'Collector ID',
        'Surface Type',
        'Surface ID',
        'Probe Type',
        'Probe Sample Date/Time',
        'Probe Depth',
        'Temperture C',
        'Sal ppt',
        'O2 percent',
        'O2 mg-l',
        'SpCond - mS',
        'Spc - mS',
        'pH',
        'Turbidity',
        'Weather Notes',
        'Samplers',
        'Other species',
    ]

    descr_fra = [
        "Année d'échantillonnage",
        "Code de la station",
        "Nom de la station",
        "Date de la mise à l'eau (aaaa-mm-jj)",
        "Date de sortie de l'eau (aaaa-mm-jj)",
        "Durée de la saison période d'immersion en semaines",
        "Description de la station",
        "Latitude du collecteur (degrés décimaux)",
        "Longitude du collecteur (degrés décimaux)",
        "Numéro du collecteur",
        "Type de surface (plaque ou pétri)",
        "Numéro du surface",
        "Modèle de la sonde",
        "Date et heure de l'échantillonnage des paramètres physico-chimiques de l'eau (aaaa-mm-jj hh:mm)",
        "Profondeur de la sonde (m)",
        "Température de l'eau au moment de l'échantillonnage (degrés C)",
        "Salinité de l'eau au moment de l'échatillonnage (ppt)",
        "Oxygène dissout (%)",
        "Oxygène dissout (mg/L)",
        "Conductance spécifique (mS)",
        "Conductivité (mS)",
        "pH",
        "Turbidité",
        "Description météo",
        "noms des échantillonneurs et nom de l’organisme responsable",
        "Autre espèces présentes sur le surface",
    ]

    descr_eng = [
        "Sample year",
        "Station code",
        "Station name",
        "Date of deployment (yyyy-mm-dd)",
        "Date of retrieval (yyyy-mm-dd)",
        "Duration in number of weeks",
        "Station description",
        "Latitude of the collector (decimal degrees)",
        "Longitude of the collector (decimal degrees)",
        "Collector identifier",
        "Surface type (plate or petri dish)",
        "Surface identifier",
        "Probe model name",
        "Date and time of probe sample (yyyy-mm-dd hh:mm)",
        "Probe depth (m)",
        "Water temperature (degrés C)",
        "Salinity (ppt)",
        "Dissolved oxygen (%)",
        "Dissolved oxygen (mg/L)",
        "Specific conductance (mS)",
        "Conductivity (mS)",
        "pH",
        "Turbidity",
        "Weather description",
        "Names of samplers and their organization affiliations",
        "Other species present on surface",
    ]

    for species in species_qs:

        first_name = species.scientific_name.split(" ")[0][:1].upper()
        if len(species.scientific_name.split(" ")) > 2:
            second_name = " ".join(species.scientific_name.split(" ")[1:])
        else:
            second_name = species.scientific_name.split(" ")[1]
        display_name = "{}. {}".format(first_name, second_name, )
        field_names.append("{} % cover".format(display_name))

        # if species id is 24 or 48, we want color morph notes as well
        if species.id in [24, 48]:
            field_names.append("{} Color Notes".format(display_name))

        descr_fra.append(
            "% de recouvrement de {}".format(species.scientific_name)
        )
        descr_eng.append(
            "% coverage of {}".format(species.scientific_name)
        )

        # if species id is 24 or 48, we want color morph notes as well
        if species.id in [24, 48]:
            descr_fra.append(
                "Patrons de couleur de {}".format(species.scientific_name)
            )
            descr_eng.append(
                "Color morph notes for {}".format(species.scientific_name)
            )

    for i in range(0, len(field_names)):
        writer.writerow([
            field_names[i],
            descr_eng[i],
            descr_fra[i],
        ])

    return response


def generate_open_data_ver_1_report(year=None):
    """
    This is a view designed for FGP / open maps view.
    :param year: int
    :return: http response
    """

    # determine the filename based on whether we are looking at all years vs. a single year
    filename = "biofouling_monitoring_report_{}.csv".format(
        year) if year and year != "None" else "biofouling_monitoring_report_all_years.csv"

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer = csv.writer(response)

    # Botrylloïdes violaceus, Botryllus shlosseri, Caprella mutica, Ciona intestinalis, Codium fragile, Membranipora membranacea, Styela clava
    species_id_list = [48, 24, 47, 23, 55, 59, 25]
    species_qs = models.Species.objects.filter(id__in=species_id_list)

    header_row = [
        'Sampling year',
        'Station code',
        'Station name',
        'Date in',
        'Date out',
        'Weeks',
        'Station Description',
        'Collector Latitude',
        'Collector Longitude',
        'Collector ID',
        'Surface Type',
        'Surface ID',
        'Probe Type',
        'Probe Sample Date/Time',
        'Probe Depth',
        'Temperture C',
        'Sal ppt',
        'O2 percent',
        'O2 mg-l',
        'SpCond - mS',
        'Spc - mS',
        'pH',
        'Turbidity',
        'Weather Notes',
        'Samplers',
        'Other species',
    ]
    for species in species_qs:
        first_name = species.scientific_name.split(" ")[0][:1].upper()
        if len(species.scientific_name.split(" ")) > 2:
            second_name = " ".join(species.scientific_name.split(" ")[1:])
        else:
            second_name = species.scientific_name.split(" ")[1]
        display_name = "{}. {}".format(first_name, second_name, )
        header_row.append("{} % cover".format(display_name))

        # if species id is 24 or 48, we want color morph notes as well
        if species.id in [24, 48]:
            header_row.append("{} Color Notes".format(display_name))

    writer.writerow(header_row)

    samples = models.Sample.objects.all()
    # if there is a year provided, filter by only this year
    if year and year != "None":
        samples = samples.filter(season=year)

    # make sure to exclude the lost lines and surfaces; this is sort of redundant since if a line is line, all surfaces should also be labelled as lost.
    surfaces = models.Surface.objects.filter(
        line__sample_id__in=[obj["id"] for obj in samples.order_by("id").values("id").distinct()],
        line__is_lost=False,
        is_lost=False,
        is_damaged=False,
    ).order_by("line__sample__date_deployed")

    for surface in surfaces:

        # Try getting hold of the last probe sample taken
        my_probe = surface.line.sample.probe_data.order_by("time_date").last()
        if my_probe:
            probe = my_probe.probe
            time_date = my_probe.time_date.strftime("%Y-%m-%d %H:%M")
            probe_depth = my_probe.probe_depth
            temp_c = my_probe.temp_c
            sal = my_probe.sal_ppt
            o2p = my_probe.o2_percent
            o2m = my_probe.o2_mgl
            spcond = my_probe.sp_cond_ms
            spc = my_probe.spc_ms
            ph = my_probe.ph
            turb = my_probe.turbidity
            weather = my_probe.weather_notes
        else:
            probe = time_date = probe_depth = temp_c = sal = o2p = o2m = spcond = spc = ph = turb = weather = None

        # summarize all of the samplers
        samplers = listrify(["{} ({})".format(obj, obj.organization) for obj in surface.line.sample.samplers.all()])
        # summarize all of the "other" species
        other_spp = listrify([sp.name_plaintext for sp in surface.species.all() if sp.id not in species_id_list])

        data_row = [
            surface.line.sample.season,
            surface.line.sample.station_id,
            surface.line.sample.station,
            surface.line.sample.date_deployed.strftime("%Y-%m-%d"),
            surface.line.sample.date_retrieved.strftime("%Y-%m-%d") if surface.line.sample.date_retrieved else None,
            surface.line.sample.weeks_deployed,
            surface.line.sample.station.site_desc,
            surface.line.latitude,
            surface.line.longitude,
            surface.line.collector,
            surface.get_surface_type_display(),
            surface.label,
            probe, time_date, probe_depth, temp_c, sal, o2p, o2m, spcond, spc, ph, turb, weather,
            samplers,
            other_spp,
        ]

        for species in species_qs:
            try:
                data_row.append(
                    floatformat(nz(models.SurfaceSpecies.objects.get(species=species, surface=surface).percent_coverage, 0) * 100, 0)
                )
            except models.SurfaceSpecies.DoesNotExist:

                data_row.append(
                    0
                )

            # if species id is 24 or 48, we want color morph notes as well
            if species.id in [24, 48]:
                try:
                    data_row.append(
                        models.SurfaceSpecies.objects.get(species=species, surface=surface).notes
                    )
                except models.SurfaceSpecies.DoesNotExist:
                    data_row.append(
                        None
                    )

        writer.writerow(data_row)

    return response


def generate_open_data_ver_1_wms_report(year, lang):
    """
    Simple report for web mapping service on FGP
    """

    # Botrylloïdes violaceus, Botryllus shlosseri, Caprella mutica, Ciona intestinalis, Codium fragile, Membranipora membranacea, Styela clava
    species_id_list = [48, 24, 47, 23, 55, 59, 25]
    species_qs = models.Species.objects.filter(id__in=species_id_list)

    filename = "station_summary_report_eng.csv" if lang == 1 else "station_summary_report_fra.csv"

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer = csv.writer(response)

    yes = "yes" if lang == 1 else "oui"
    no = "no" if lang == 1 else "non"

    header_row = [
        'seasons' if lang == 1 else "saisons",
        'station_code' if lang == 1 else "code_de_station",
        'station_name' if lang == 1 else "nom_de_station",
        'station_province' if lang == 1 else "province_de_station",
        'station_description' if lang == 1 else "description_de_station",
        'station_latitude' if lang == 1 else "latitude_de_station",
        'station_longitude' if lang == 1 else "longitude_de_station",
        'list_of_other_species_observed' if lang == 1 else "liste_des_espèces_observées",
    ]

    for species in species_qs:
        first_name = species.scientific_name.split(" ")[0][:1].upper()
        if len(species.scientific_name.split(" ")) > 2:
            second_name = " ".join(species.scientific_name.split(" ")[1:])
        else:
            second_name = species.scientific_name.split(" ")[1]
        display_name = "{}_{}".format(first_name, second_name, )
        my_str = "detected" if lang == 1 else "détecté"
        header_row.append("{}_{}".format(display_name, my_str))

    writer.writerow(header_row)

    samples = models.Sample.objects.all()
    # if there is a year provided, filter by only this year
    if year and year != "None":
        samples = samples.filter(season=int(year))

    stations = [models.Station.objects.get(pk=obj["station"]) for obj in samples.order_by("station").values("station").distinct()]
    # make sure to exclude the lost lines and surfaces; this is sort of redundant since if a line is line, all surfaces should also be labelled as lost.
    surfacespecies = models.SurfaceSpecies.objects.filter(
        surface__line__sample_id__in=[obj["id"] for obj in samples.order_by("id").values("id").distinct()],
        surface__line__is_lost=False,
        surface__is_lost=False,
        surface__is_damaged=False,
    )

    for station in stations:
        other_spp = listrify([models.Species.objects.get(pk=obj["species"]).name_plaintext for obj in
                              surfacespecies.filter(surface__line__sample__station=station).order_by("species").values("species").distinct()
                              if obj["species"] not in species_id_list])
        seasons = listrify(
            [obj["surface__line__sample__season"] for obj in
             surfacespecies.filter(surface__line__sample__station=station).order_by("surface__line__sample__season").values(
                 "surface__line__sample__season").distinct()])
        data_row = [
            seasons,
            station.id,
            station.station_name,
            station.province.abbrev_eng if lang == 1 else station.province.abbrev_fre,
            station.site_desc,
            station.latitude,
            station.longitude,
            other_spp,
        ]

        for species in species_qs:
            spp_count = surfacespecies.filter(
                surface__line__sample__station=station,
                species=species,
            ).count()
            if spp_count > 0:
                data_row.append(yes)
            else:
                data_row.append(no)

        writer.writerow(data_row)

    return response


def generate_gc_cpue_report(year=None):
    """Returns a generator for an HTTP Streaming Response"""
    header_row = [
        'Year',
        'Estuary',
        'Site',
        'Sample ID',
        'Traps set',
        'Traps fished',
        'Trap #',
        'Sex',
        'Width',
    ]

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    yield writer.writerow(header_row)

    filter_kwargs = {}
    if year:
        filter_kwargs["trap__sample__season"] = year

    for c in models.Catch.objects.filter(**filter_kwargs).filter(species_id=26):
        data_row = [
            c.trap.sample.season,
            c.trap.sample.site.estuary.name,
            c.trap.sample.site.code,
            c.trap.sample.id,
            c.trap.sample.traps_set.strftime("%Y-%m-%d") if c.trap.sample.traps_set else "",
            c.trap.sample.traps_fished.strftime("%Y-%m-%d") if c.trap.sample.traps_fished else "",
            c.trap.trap_number,
            c.get_sex_display(),
            c.width,
        ]
        yield writer.writerow(data_row)


def generate_gc_envr_report(year):
    # figure out the filename
    target_dir = os.path.join(settings.BASE_DIR, 'media', 'grais', 'temp')
    target_file = "temp_data_export_{}.xlsx".format(timezone.now().strftime("%Y-%m-%d"))
    target_file_path = os.path.join(target_dir, target_file)
    target_url = os.path.join(settings.MEDIA_ROOT, 'grais', 'temp', target_file)

    # create workbook and worksheets
    workbook = xlsxwriter.Workbook(target_file_path)

    # create formatting variables
    header_format = workbook.add_format({'bold': True, "align": 'normal', "text_wrap": True})
    normal_format = workbook.add_format({"align": 'normal', "text_wrap": True, })

    # define a worksheet
    my_ws = workbook.add_worksheet(name='sheet1')

    # define the header
    header_row = [
        'Estuary',
        'Site',
        'Sample ID',
        'Date',
        'Temperature (C)',
        'Salinity',
        'Tide description',
    ]
    my_ws.write_row(0, 0, header_row, header_format)

    i = 1
    # create the col_max column to store the length of each header
    # should be a maximum column width to 100
    col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header_row]
    for obj in models.GCProbeMeasurement.objects.filter(sample__season=year):
        data_row = [
            obj.sample.site.estuary.name,
            obj.sample.site.code,
            obj.sample.id,
            obj.time_date.strftime("%Y-%m-%d") if obj.time_date else "",
            obj.temp_c,
            obj.sal,
            obj.tide_description,
        ]

        # adjust the width of the columns based on the max string length in each col
        ## replace col_max[j] if str length j is bigger than stored value

        j = 0
        for d in data_row:
            # if new value > stored value... replace stored value
            if len(str(d)) > col_max[j]:
                if len(str(d)) < 75:
                    col_max[j] = len(str(d))
                else:
                    col_max[j] = 75
            j += 1

        my_ws.write_row(i, 0, data_row, normal_format)
        i += 1

    # set column widths
    for j in range(0, len(col_max)):
        my_ws.set_column(j, j, width=col_max[j] * 1.1)

    workbook.close()
    return target_url


def generate_gc_sites_report():
    # figure out the filename
    target_dir = os.path.join(settings.BASE_DIR, 'media', 'grais', 'temp')
    target_file = "temp_data_export_{}.xlsx".format(timezone.now().strftime("%Y-%m-%d"))
    target_file_path = os.path.join(target_dir, target_file)
    target_url = os.path.join(settings.MEDIA_ROOT, 'grais', 'temp', target_file)

    # create workbook and worksheets
    workbook = xlsxwriter.Workbook(target_file_path)

    # create formatting variables
    header_format = workbook.add_format({'bold': True, "align": 'normal', "text_wrap": True})
    normal_format = workbook.add_format({"align": 'normal', "text_wrap": True, })

    # define a worksheet
    my_ws = workbook.add_worksheet(name='sheet1')

    # define the header
    header_row = [
        'Estuary name',
        'Estuary description',
        'Province',
        'Site name',
        'Site code',
        'Site description',
        'Latitutde',
        'Longitude',
    ]
    my_ws.write_row(0, 0, header_row, header_format)

    i = 1
    # create the col_max column to store the length of each header
    # should be a maximum column width to 100
    col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header_row]
    for obj in models.Site.objects.all():
        data_row = [
            obj.estuary.name,
            obj.estuary.description,
            obj.estuary.province.abbrev_eng,
            obj.name,
            obj.code,
            obj.description,
            obj.latitude,
            obj.longitude,
        ]

        # adjust the width of the columns based on the max string length in each col
        ## replace col_max[j] if str length j is bigger than stored value

        j = 0
        for d in data_row:
            # if new value > stored value... replace stored value
            if len(str(d)) > col_max[j]:
                if len(str(d)) < 75:
                    col_max[j] = len(str(d))
                else:
                    col_max[j] = 75
            j += 1

        my_ws.write_row(i, 0, data_row, normal_format)
        i += 1

    # set column widths
    for j in range(0, len(col_max)):
        my_ws.set_column(j, j, width=col_max[j] * 1.1)

    workbook.close()
    return target_url


def generate_gc_gravid_green_crabs_report():
    # figure out the filename
    target_dir = os.path.join(settings.BASE_DIR, 'media', 'temp')
    target_file = "temp_data_export_{}.xlsx".format(timezone.now().strftime("%Y-%m-%d"))
    target_file_path = os.path.join(target_dir, target_file)
    target_url = os.path.join(settings.MEDIA_ROOT, 'temp', target_file)

    # create workbook and worksheets
    workbook = xlsxwriter.Workbook(target_file_path, options=dict(remove_timezone=True))

    # create formatting variables
    header_format = workbook.add_format({'bold': True, "align": 'normal', "text_wrap": True})
    normal_format = workbook.add_format({"align": 'normal', "text_wrap": True, })

    # define a worksheet
    my_ws = workbook.add_worksheet(name='sheet1')

    # define the header
    qs = models.Catch.objects.filter(species__aphia_id=107381, egg_color__isnull=False)

    if qs.exists():
        header_row = [
            "estuary_name",
            "estuary_province",
            "site_name",
            "site_code",
            "datetime_traps_set",
            "datetime_traps_fished",
            "site_latitude",
            "site_longitude",
            "sample.id",
            "trap_number",
            "trap_type",
            "bait_type",
            "gps_waypoint",
            "trap_notes",
            "total_green_crab_wt_kg",
            "catch_id",
            "species",
            "sex",
            "egg_color",
            "count",
        ]
        my_ws.write_row(0, 0, header_row, header_format)

        i = 1
        # create the col_max column to store the length of each header
        # should be a maximum column width to 100
        col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in header_row]
        for obj in qs:
            data_row = [
                obj.trap.sample.site.estuary.name,
                str(obj.trap.sample.site.estuary.province),
                obj.trap.sample.site.name,
                obj.trap.sample.site.code,
                obj.trap.sample.traps_set.strftime("%Y-%m-%d") if obj.trap.sample.traps_set else "",
                obj.trap.sample.traps_fished.strftime("%Y-%m-%d") if obj.trap.sample.traps_fished else "",
                obj.trap.sample.site.latitude,
                obj.trap.sample.site.longitude,
                obj.trap.sample.id,
                obj.trap.trap_number,
                obj.trap.get_trap_type_display(),
                str(obj.trap.bait_type),
                obj.trap.gps_waypoint,
                obj.trap.notes,
                obj.trap.total_green_crab_wt_kg,
                obj.id,
                str(obj.species),
                obj.get_sex_display(),
                obj.egg_color,
                obj.count,
            ]

            # adjust the width of the columns based on the max string length in each col
            ## replace col_max[j] if str length j is bigger than stored value

            j = 0
            for d in data_row:
                # if new value > stored value... replace stored value
                if len(str(d)) > col_max[j]:
                    if len(str(d)) < 75:
                        col_max[j] = len(str(d))
                    else:
                        col_max[j] = 75
                j += 1

            my_ws.write_row(i, 0, data_row, normal_format)
            i += 1

        # set column widths
        for j in range(0, len(col_max)):
            my_ws.set_column(j, j, width=col_max[j] * 1.1)

    workbook.close()
    return target_url


def generate_biofouling_station_report():
    # figure out the filename
    target_dir = os.path.join(settings.BASE_DIR, 'media', 'temp')
    target_file = "temp_data_export_{}.xlsx".format(timezone.now().strftime("%Y-%m-%d"))
    target_file_path = os.path.join(target_dir, target_file)
    target_url = os.path.join(settings.MEDIA_ROOT, 'temp', target_file)

    # create workbook and worksheets
    workbook = xlsxwriter.Workbook(target_file_path, options=dict(remove_timezone=True))

    # create formatting variables
    header_format = workbook.add_format({'bold': True, "align": 'normal', "text_wrap": True})
    normal_format = workbook.add_format({"align": 'normal', "text_wrap": True, })

    # define a worksheet
    my_ws = workbook.add_worksheet(name='stations')

    # define the header
    qs = models.Station.objects.all()

    if qs.exists():
        fields = [
            "id",
            "station_name",
            "province",
            "depth",
            "site_desc",
            "contact_information",
            "notes",
            "latitude",
            "longitude",
            "years|years sampled",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
        ]
        header_row = [get_verbose_label(qs.first(), field) for field in fields]

        my_ws.write_row(0, 0, header_row, header_format)

        i = 1
        # create the col_max column to store the length of each header
        # should be a maximum column width to 100
        col_max = [len(str(d)) if len(str(d)) <= 100 else 100 for d in fields]
        for obj in qs:
            data_row = [str(get_field_value(obj, field)) for field in fields]

            # adjust the width of the columns based on the max string length in each col
            ## replace col_max[j] if str length j is bigger than stored value

            j = 0
            for d in data_row:
                # if new value > stored value... replace stored value
                if len(str(d)) > col_max[j]:
                    if len(str(d)) < 75:
                        col_max[j] = len(str(d))
                    else:
                        col_max[j] = 75
                j += 1

            my_ws.write_row(i, 0, data_row, normal_format)
            i += 1

        # set column widths
        for j in range(0, len(col_max)):
            my_ws.set_column(j, j, width=col_max[j] * 1.1)

    workbook.close()
    return target_url
