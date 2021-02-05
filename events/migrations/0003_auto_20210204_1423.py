# Generated by Django 3.1.2 on 2021-02-04 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_auto_20210201_1415'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='note',
            options={'ordering': ['is_complete', '-updated_at']},
        ),
        migrations.AlterField(
            model_name='event',
            name='type',
            field=models.IntegerField(choices=[(1, 'CSAS Regional Advisory Process (RAP)'), (2, 'CSAS Science Management Meeting'), (2, 'CSAS Steering Committee Meeting'), (9, 'other')], verbose_name='type of event'),
        ),
        migrations.AlterField(
            model_name='invitee',
            name='organization',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Association'),
        ),
        migrations.AlterField(
            model_name='invitee',
            name='role',
            field=models.IntegerField(choices=[(1, 'attendee'), (2, 'chair'), (3, 'expert')], default=1, verbose_name='Function'),
        ),
        migrations.AlterField(
            model_name='invitee',
            name='status',
            field=models.IntegerField(choices=[(1, 'accepted'), (2, 'declined'), (9, 'not response')], default=1, verbose_name='status'),
        ),
    ]
