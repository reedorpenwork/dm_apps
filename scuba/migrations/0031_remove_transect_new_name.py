# Generated by Django 3.2.5 on 2021-12-06 17:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scuba', '0030_alter_transect_unique_together'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transect',
            name='new_name',
        ),
    ]
