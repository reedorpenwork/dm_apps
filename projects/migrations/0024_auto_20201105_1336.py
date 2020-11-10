# Generated by Django 3.1.2 on 2020-11-05 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0023_auto_20201105_1325'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='requires_specialized_equipement',
            new_name='requires_specialized_equipment',
        ),
        migrations.AlterField(
            model_name='project',
            name='coip_reference_id',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='If this project links to a ship time request in COIP, please include the COIP application number here.'),
        ),
    ]
