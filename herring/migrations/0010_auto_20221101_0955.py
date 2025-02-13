# Generated by Django 3.2.14 on 2022-11-01 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herring', '0009_auto_20221101_0943'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='species',
            options={'ordering': ['name'], 'verbose_name_plural': 'species'},
        ),
        migrations.RemoveField(
            model_name='species',
            name='code',
        ),
        migrations.AlterField(
            model_name='species',
            name='aphia_id',
            field=models.IntegerField(unique=True, verbose_name='WoRMS AphiaID'),
        ),
    ]
