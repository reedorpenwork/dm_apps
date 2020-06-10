# Generated by Django 2.2.2 on 2020-05-13 18:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0008_trippurpose'),
    ]

    operations = [
        migrations.AddField(
            model_name='conference',
            name='trip_purpose',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='trips', to='travel.TripPurpose', verbose_name='trip purpose'),
        ),
    ]
