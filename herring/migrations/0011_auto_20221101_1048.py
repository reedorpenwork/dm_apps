# Generated by Django 3.2.14 on 2022-11-01 13:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herring', '0010_auto_20221101_0955'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='species',
            name='min_length',
        ),
        migrations.RemoveField(
            model_name='species',
            name='min_weight',
        ),
    ]
