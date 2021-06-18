# Generated by Django 3.2 on 2021-06-01 12:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shared_models', '0014_auto_20210511_1253'),
        ('masterlist', '0007_auto_20210201_1413'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='province',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='shared_models.province', verbose_name='province/territory'),
        ),
    ]
