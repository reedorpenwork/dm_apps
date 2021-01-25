# Generated by Django 3.1.2 on 2021-01-15 14:33

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scuba', '0020_auto_20210112_0725'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='latitude_d',
            field=models.IntegerField(blank=True, null=True, verbose_name='latitude (degrees)'),
        ),
        migrations.AddField(
            model_name='site',
            name='latitude_mm',
            field=models.FloatField(blank=True, null=True, verbose_name='latitude (minutes)'),
        ),
        migrations.AddField(
            model_name='site',
            name='longitude_d',
            field=models.IntegerField(blank=True, null=True, verbose_name='longitude (degrees)'),
        ),
        migrations.AddField(
            model_name='site',
            name='longitude_mm',
            field=models.FloatField(blank=True, null=True, verbose_name='longitude (minutes)'),
        ),
        migrations.AlterField(
            model_name='observation',
            name='certainty_rating',
            field=models.IntegerField(choices=[(1, 'certain'), (0, 'uncertain')], default=1, verbose_name='length certainty'),
        ),
        migrations.AlterField(
            model_name='section',
            name='interval',
            field=models.IntegerField(choices=[(1, '1 (0-5m)'), (2, '2 (5-10m)'), (3, '3 (10-15m)'), (4, '4 (15-20m)'), (5, '5 (20-25m)'), (6, '6 (25-30m)'), (7, '7 (30-35m)'), (8, '8 (35-40m)'), (9, '9 (40-45m)'), (10, '10 (45-50m)'), (11, '11 (50-55m)'), (12, '12 (55-60m)'), (13, '13 (60-65m)'), (14, '14 (65-70m)'), (15, '15 (70-75m)'), (16, '16 (75-80m)'), (17, '17 (80-85m)'), (18, '18 (85-90m)'), (19, '19 (90-95m)'), (20, '20 (95-100m)')], validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(20)], verbose_name='5m interval [1-20]'),
        ),
        migrations.AlterField(
            model_name='section',
            name='percent_algae',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)], verbose_name='algae [0-1]'),
        ),
        migrations.AlterField(
            model_name='section',
            name='percent_cobble',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)], verbose_name='cobble [0-1]'),
        ),
        migrations.AlterField(
            model_name='section',
            name='percent_gravel',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)], verbose_name='gravel [0-1]'),
        ),
        migrations.AlterField(
            model_name='section',
            name='percent_hard',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)], verbose_name='hard [0-1]'),
        ),
        migrations.AlterField(
            model_name='section',
            name='percent_mud',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)], verbose_name='mud [0-1]'),
        ),
        migrations.AlterField(
            model_name='section',
            name='percent_pebble',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)], verbose_name='pebble [0-1]'),
        ),
        migrations.AlterField(
            model_name='section',
            name='percent_sand',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)], verbose_name='sand [0-1]'),
        ),
        migrations.AlterField(
            model_name='site',
            name='latitude',
            field=models.FloatField(blank=True, editable=False, null=True, verbose_name='latitude (decimal degrees)'),
        ),
        migrations.AlterField(
            model_name='site',
            name='longitude',
            field=models.FloatField(blank=True, editable=False, null=True, verbose_name='longitude (decimal degrees)'),
        ),
    ]
