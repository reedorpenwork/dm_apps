# Generated by Django 3.2.13 on 2022-06-07 01:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0010_auto_20220606_2122'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='province',
            field=models.CharField(blank=True, max_length=7, null=True, verbose_name='postal code'),
        ),
    ]
