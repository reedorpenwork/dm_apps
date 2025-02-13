# Generated by Django 3.2.13 on 2022-06-03 17:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cars', '0003_auto_20220603_1135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='address',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='address'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='primary_driver',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='reservations', to=settings.AUTH_USER_MODEL, verbose_name='primary driver'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='vehicle',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='reservations', to='cars.vehicle', verbose_name='vehicle'),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='is_active',
            field=models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=True, help_text='Vehicles that are not in commission will not show up in the reservation list', verbose_name='is in commission?'),
        ),
    ]
