# Generated by Django 3.2.14 on 2022-12-01 15:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trapnet', '0003_auto_20221129_1620'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sample',
            name='didymo',
            field=models.IntegerField(blank=True, choices=[(None, 'Not checked'), (0, 'Absent'), (1, 'Present')], null=True, verbose_name='presence / absence of Didymosphenia geminata'),
        ),
        migrations.AlterField(
            model_name='sample',
            name='monitoring_program',
            field=models.ForeignKey(blank=True, help_text='The sample was collected under which monitoring program', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='samples', to='trapnet.monitoringprogram', verbose_name='monitoring program'),
        ),
    ]
