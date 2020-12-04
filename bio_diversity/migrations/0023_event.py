# Generated by Django 3.1.2 on 2020-12-04 17:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bio_diversity', '0022_eventcode_facilitycode_personnelcode_rolecode_team'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(max_length=32, verbose_name='Created By')),
                ('created_date', models.DateField(verbose_name='Created Date')),
                ('evnt_start', models.DateField(verbose_name='Event start date')),
                ('evnt_starttime', models.TimeField(blank=True, null=True, verbose_name='Event start time')),
                ('evnt_end', models.DateField(verbose_name='Event end date')),
                ('evnt_endtime', models.TimeField(blank=True, null=True, verbose_name='Event end time')),
                ('comments', models.CharField(blank=True, max_length=2000, null=True, verbose_name='Comments')),
                ('evntc_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='bio_diversity.eventcode', verbose_name='Event Code')),
                ('facic_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='bio_diversity.facilitycode', verbose_name='Facility Code')),
                ('perc_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='bio_diversity.personnelcode', verbose_name='Personnel Code')),
                ('prog_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='bio_diversity.program', verbose_name='Program')),
                ('team_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='bio_diversity.team', verbose_name='Team')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
