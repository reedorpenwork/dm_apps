# Generated by Django 3.2 on 2021-04-22 10:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shared_models', '0010_alter_person_dmapps_user'),
        ('csas2', '0006_auto_20210422_0719'),
    ]

    operations = [
        migrations.AddField(
            model_name='process',
            name='fiscal_year',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='processes', to='shared_models.fiscalyear', verbose_name='fiscal year'),
        ),
    ]
