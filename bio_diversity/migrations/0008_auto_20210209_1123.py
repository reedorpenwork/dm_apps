# Generated by Django 3.1.2 on 2021-02-09 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bio_diversity', '0007_individualdet_indvd_valid'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupdet',
            name='grpd_valid',
            field=models.BooleanField(default='True', verbose_name='Detail still valid?'),
        ),
        migrations.AlterField(
            model_name='groupdet',
            name='det_val',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Value'),
        ),
    ]
