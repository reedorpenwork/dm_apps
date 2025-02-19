# Generated by Django 3.2.13 on 2022-06-28 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csas2', '0010_auto_20220531_2326'),
    ]

    operations = [
        migrations.AlterField(
            model_name='termsofreference',
            name='status',
            field=models.IntegerField(choices=[(10, 'Draft'), (20, 'Under review'), (30, 'Awaiting changes'), (35, 'Approved'), (40, 'Awaiting posting'), (50, 'Posted')], default=10, editable=False, verbose_name='status'),
        ),
        migrations.AlterUniqueTogether(
            name='torreviewer',
            unique_together=set(),
        ),
    ]
