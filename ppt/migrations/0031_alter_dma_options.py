# Generated by Django 3.2.10 on 2022-04-14 13:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ppt', '0030_auto_20220413_1140'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dma',
            options={'ordering': ['project__section__division__branch__sector__region', 'project__section__division', 'project__section'], 'verbose_name': 'Data Management Agreement'},
        ),
    ]
