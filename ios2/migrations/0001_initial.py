# Generated by Django 2.1.4 on 2019-04-02 17:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Deployment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mooring', models.CharField(blank=True, max_length=200, null=True, verbose_name='mooring name')),
                ('mooring_number', models.CharField(blank=True, max_length=200, null=True, verbose_name='mooring number')),
                ('deploy_time', models.DateTimeField(blank=True, null=True, verbose_name='deploy time (UTC)')),
                ('recover_time', models.DateTimeField(blank=True, null=True, verbose_name='recover time (UTC)')),
                ('lat', models.TextField(blank=True, null=True, verbose_name='lat')),
                ('lon', models.TextField(blank=True, null=True, verbose_name='lon')),
                ('depth', models.TextField(blank=True, null=True, verbose_name='depth')),
                ('comments', models.TextField(blank=True, null=True, verbose_name='comments')),
            ],
            options={
                'ordering': ['mooring'],
            },
        ),
        migrations.CreateModel(
            name='Instrument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instrument_type', models.CharField(choices=[('CTD', 'CTD'), ('ADCP', 'ADCP')], default='CTD', max_length=20, verbose_name='Instrument Type')),
                ('serial_number', models.CharField(default='0000', max_length=20, verbose_name='Serial ID')),
                ('purchase_date', models.DateField(blank=True, null=True, verbose_name='Purchase Date')),
                ('project_title', models.TextField(blank=True, null=True, verbose_name='Project title')),
                ('scientist', models.TextField(blank=True, null=True, verbose_name='Scientist')),
                ('date_of_last_service', models.DateField(blank=True, null=True, verbose_name='Last Service Date')),
                ('date_of_next_service', models.DateField(blank=True, null=True, verbose_name='Next Service Date')),
                ('submitted', models.BooleanField(default=False, verbose_name='Submit instrument for review')),
                ('test1', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='testa', to='ios2.Deployment', verbose_name='test1')),
            ],
            options={
                'ordering': ['instrument_type', 'serial_number', 'purchase_date', 'project_title'],
            },
        ),
        migrations.AddField(
            model_name='deployment',
            name='instruments',
            field=models.ManyToManyField(related_name='ins2', to='ios2.Instrument', verbose_name='instruments'),
        ),
        migrations.AlterUniqueTogether(
            name='instrument',
            unique_together={('instrument_type', 'serial_number')},
        ),
        migrations.AlterUniqueTogether(
            name='deployment',
            unique_together={('mooring', 'mooring_number')},
        ),
    ]
