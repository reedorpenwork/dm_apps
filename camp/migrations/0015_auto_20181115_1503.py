# Generated by Django 2.0.4 on 2018-11-15 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('camp', '0014_auto_20181114_1055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='species',
            name='common_name_eng',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='english name'),
        ),
        migrations.AlterField(
            model_name='species',
            name='common_name_fre',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='french name'),
        ),
    ]
