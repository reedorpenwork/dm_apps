# Generated by Django 3.2.14 on 2022-12-07 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trapnet', '0011_auto_20221206_1019'),
    ]

    operations = [
        migrations.AddField(
            model_name='trapnetsample',
            name='sea_lice',
            field=models.IntegerField(blank=True, choices=[(None, 'None'), (1, '< 5'), (2, '5-15'), (3, '15-50'), (4, '> 50')], null=True),
        ),
    ]
