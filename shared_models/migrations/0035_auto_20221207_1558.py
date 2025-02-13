# Generated by Django 3.2.14 on 2022-12-07 19:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shared_models', '0034_auto_20221017_1301'),
    ]

    operations = [
        migrations.AddField(
            model_name='fishingarea',
            name='description',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='river',
            name='fishing_area',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='rivers', to='shared_models.fishingarea'),
        ),
    ]
