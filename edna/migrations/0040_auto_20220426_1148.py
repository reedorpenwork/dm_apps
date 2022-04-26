# Generated by Django 3.2.10 on 2022-04-26 14:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('edna', '0039_auto_20220425_2015'),
    ]

    operations = [
        migrations.AddField(
            model_name='filter',
            name='end_datetime',
            field=models.DateTimeField(blank=True, null=True, verbose_name='end time'),
        ),
        migrations.AlterField(
            model_name='extractionbatch',
            name='default_collection',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='edna.collection', verbose_name='project'),
        ),
        migrations.AlterField(
            model_name='filter',
            name='duration_min',
            field=models.IntegerField(blank=True, editable=False, null=True, verbose_name='filtration duration (min)'),
        ),
        migrations.AlterField(
            model_name='filter',
            name='start_datetime',
            field=models.DateTimeField(verbose_name='start time'),
        ),
        migrations.AlterField(
            model_name='filtrationbatch',
            name='default_collection',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='edna.collection', verbose_name='project'),
        ),
        migrations.AlterField(
            model_name='pcrbatch',
            name='default_collection',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='edna.collection', verbose_name='project'),
        ),
    ]
