# Generated by Django 2.2.2 on 2020-03-24 17:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('whalesdb', '0003_auto_20200324_0707'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rstrecordingstage',
            name='rsc',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='stages', to='whalesdb.RscRecordingSchedule', verbose_name='Schedule'),
        ),
    ]
