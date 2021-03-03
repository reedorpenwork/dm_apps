# Generated by Django 3.1.2 on 2021-03-02 20:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shared_models', '0004_auto_20210126_1540'),
        ('spot', '0008_auto_20210302_1136'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ['agreement_number', 'name', 'region', 'primary_river', 'target_species', 'DFO_project_authority']},
        ),
        migrations.RemoveField(
            model_name='project',
            name='primary_river',
        ),
        migrations.AddField(
            model_name='project',
            name='primary_river',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='primary_river', to='shared_models.river', verbose_name='primary river'),
        ),
    ]
