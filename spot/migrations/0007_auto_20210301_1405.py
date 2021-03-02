# Generated by Django 3.1.2 on 2021-03-01 22:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('spot', '0006_auto_20210301_1239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='first_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='first name'),
        ),
        migrations.AlterField(
            model_name='person',
            name='organization',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='spot.organization', verbose_name='organization'),
        ),
    ]
