import csv
import datetime
import os

from django.conf import settings
from django.core import serializers
from django.core.files import File
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import activate

from ihub import models
from lib.functions.custom_functions import listrify
from lib.templatetags.custom_filters import nz
from masterlist import models as ml_models
from shared_models import models as shared_models


def export_fixtures():
    """ a simple function to expor the important lookup tables. These fixutre will be used for testing and also for seeding new instances"""
    fixtures_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../fixtures')
    models_to_export = [
        models.EntryType,
        models.Status,
        models.FundingPurpose,
        models.FundingProgram,
        ml_models.Nation,
        ml_models.RelationshipRating,
        ml_models.Grouping,
        shared_models.FiscalYear,
    ]
    for model in models_to_export:
        data = serializers.serialize("json", model.objects.all())
        my_label = model._meta.db_table
        f = open(os.path.join(fixtures_dir, f'{my_label}.json'), 'w')
        myfile = File(f)
        myfile.write(data)
        myfile.close()


def clean_masterlist():
    for contact in ml_models.Person.objects.all():
        if not contact.project_people.count():
            try:
                contact.delete()
            except:
                print("cannot delete contact")

    for org in ml_models.Organization.objects.all():
        if not org.members.count() and not org.entries.count() and not org.projects.count():
            try:
                org.delete()
            except:
                print("cannot delete org")


def digest_qc_data():
    # open the csv we want to read
    my_target_data_file = os.path.join(settings.BASE_DIR, 'ihub', 'qc_data_april_23_2021.csv')
    with open(my_target_data_file, 'r') as csv_read_file:
        my_csv = csv.DictReader(csv_read_file)

        # stuff that has to happen before running the loop
        qc_region = shared_models.Region.objects.get(name="Quebec")
        models.Status.objects.get_or_create(name="cancelled")  # make sure the cancelled status exists
        activate("fr")
        for row in my_csv:

            # title
            entry, created = models.Entry.objects.get_or_create(
                title=row["title"].strip(),
            )
            if created:
                entry.old_id = entry.id
                entry.save()

            entry.regions.add(qc_region)

            # Org...
            # there can be up to 9 organizations
            org_cols = ["org1", "org2", "org3", "org4", "org5", "org6", "org7", "org8", "org9", ]
            for org_col in org_cols:
                org_txt = nz(row[org_col].strip(), None)
                if org_txt and org_txt != "":
                    org = None
                    qs = ml_models.Organization.objects.filter(Q(name_eng__icontains=org_txt) | Q(
                        abbrev__icontains=org_txt))  # in term "David Fishman" et "David Smith" --> d == True | avid == True ishm
                    if not qs.exists():  # pas resultat
                        # then we just create a new org
                        org = ml_models.Organization.objects.create(name_eng=org_txt)
                        print(f"Creating new organization: {org.name_eng} ({org.id})")  # --> http://dmapps{reverse('ihub:org_detail', args=[org.id])}")
                    elif qs.count() == 1:
                        # means we have a direct hit
                        org = qs.first()
                    else:
                        print(f"Found multiple organizations for {org_txt}: {listrify([str(o) for o in qs])}")
                    if org:
                        org.regions.add(qc_region)
                        org.grouping.add(7)
                        entry.organizations.add(org)

            # Sector
            sector, created = ml_models.Sector.objects.get_or_create(
                name=row["sector"].strip(),
                region=qc_region,
            )
            entry.sectors.add(sector)

            # type
            try:
                type = models.EntryType.objects.get(name__iexact=row["type"].strip())
            except:
                type = None
                if row["type"] == 'Mobilisation':
                    type = models.EntryType.objects.get(name__iexact="engagement")
                else:
                    print("can't find type: ", row["type"].strip())
            entry.entry_type = type

            # status
            status_txt = nz(row["status"].strip(), None)
            if status_txt:
                try:
                    status = models.Status.objects.get(name__icontains=status_txt)
                except:
                    if 'active' in status_txt.lower():
                        status = models.Status.objects.get(pk=1)
                    else:
                        status = None
                        print("can't find status: ", row["status"].strip())
                entry.status = status

            # date1
            dt = None
            date1 = nz(row["date1"], None)
            if date1:
                if len(date1.split("/")) == 3:
                    dt = datetime.datetime.strptime(date1, "%m/%d/%Y")
                    dt = timezone.make_aware(dt, timezone.get_current_timezone())
                    entry.initial_date = dt
                else:
                    print(f'Cannot parse start date for Entry #{entry.id}: {date1}')

            # date2
            dt = None
            date2 = nz(row["date2"], None)
            if date2:
                if len(date2.split("/")) == 3:
                    dt = datetime.datetime.strptime(date2, "%m/%d/%Y")
                    dt = timezone.make_aware(dt, timezone.get_current_timezone())
                    entry.anticipated_end_date = dt
                else:
                    print(f'Cannot parse start date for Entry #{entry.id}: {date2}')

            proponent = nz(row['promoteur'], None)
            if proponent:
                entry.proponent = proponent

            entry.save()

            # contact
            i_list = [1, 2, 3, 4]
            for i in i_list:
                name = nz(row['contact' + str(i)], None)
                if name:
                    person, created = models.EntryPerson.objects.get_or_create(
                        entry=entry,
                        name=name,
                        organization=nz(row['contact_org' + str(i)], "DFO-MPO"),
                        role=2
                    )

            i_list = [1, 2, 3, 4, 5, 6]
            for i in i_list:
                comment = nz(row['comment' + str(i)], None)
                if comment:
                    models.EntryNote.objects.get_or_create(
                        entry=entry,
                        type=3,
                        note=comment,
                    )

            suivi = nz(row["suivi"], None)
            if suivi:
                models.EntryNote.objects.get_or_create(
                    entry=entry,
                    type=4,
                    note=suivi,
                )


def delete_all_data():
    models.Entry.objects.filter(old_id__isnull=False).delete()
