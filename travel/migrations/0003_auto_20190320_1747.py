# Generated by Django 2.1.4 on 2019-03-20 20:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0002_auto_20190318_2133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='section',
            field=models.ForeignKey(blank=True, limit_choices_to={'division__branch': 1}, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='shared_models.Section', verbose_name='DFO section'),
        ),
    ]
