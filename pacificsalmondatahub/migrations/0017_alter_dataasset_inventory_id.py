# Generated by Django 3.2.15 on 2022-12-22 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pacificsalmondatahub', '0016_auto_20221222_1144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataasset',
            name='Inventory_ID',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
