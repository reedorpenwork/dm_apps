# Generated by Django 3.2.10 on 2022-03-29 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grais', '0008_auto_20220301_0941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gcprobemeasurement',
            name='cond_ms',
            field=models.FloatField(blank=True, null=True, verbose_name='Conductivity (µS)'),
        ),
        migrations.AlterField(
            model_name='gcprobemeasurement',
            name='sp_cond_ms',
            field=models.FloatField(blank=True, null=True, verbose_name='Specific conductance (µS)'),
        ),
        migrations.AlterField(
            model_name='probemeasurement',
            name='sp_cond_ms',
            field=models.FloatField(blank=True, null=True, verbose_name='Specific conductance (µS)'),
        ),
        migrations.AlterField(
            model_name='probemeasurement',
            name='spc_ms',
            field=models.FloatField(blank=True, null=True, verbose_name='Conductivity (µS)'),
        ),
    ]
