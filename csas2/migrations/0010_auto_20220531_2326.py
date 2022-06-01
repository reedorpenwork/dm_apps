# Generated by Django 3.2.13 on 2022-06-01 02:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('csas2', '0009_meeting_is_somp_submitted'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='meetingfile',
            name='is_somp',
        ),
        migrations.AlterField(
            model_name='document',
            name='lead_office',
            field=models.ForeignKey(blank=True, help_text='The Lead CSAS office will process approvals and translation and will be listed on the cover page of the publication', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='documents', to='csas2.csasoffice', verbose_name='lead CSAS office'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='chair_comments',
            field=models.TextField(blank=True, help_text='Does the chair have comments to be captured OR passed on to NCR following the peer-review meeting.', null=True, verbose_name='post-meeting chair comments'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='is_somp_submitted',
            field=models.BooleanField(default=False, editable=False, verbose_name='have the SoMP been submitted?'),
        ),
    ]
