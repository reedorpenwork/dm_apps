# Generated by Django 3.2 on 2021-05-12 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('whalesdb', '0013_auto_20210421_1354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rcichannelinfo',
            name='rci_volts',
            field=models.DecimalField(blank=True, decimal_places=20, max_digits=22, null=True, verbose_name='Volts per bit'),
        ),
    ]
