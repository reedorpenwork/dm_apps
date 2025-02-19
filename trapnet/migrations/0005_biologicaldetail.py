# Generated by Django 3.2.14 on 2022-12-02 14:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('trapnet', '0004_auto_20221201_1135'),
    ]

    operations = [
        migrations.CreateModel(
            name='BiologicalDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('adipose_condition', models.IntegerField(blank=True, choices=[(None, 'Not checked'), (0, 'Absent'), (1, 'Present')], null=True, verbose_name='adipose condition')),
                ('fork_length', models.FloatField(blank=True, null=True, verbose_name='fork length (mm)')),
                ('fork_length_bin_interval', models.FloatField(default=1, verbose_name='fork length bin interval (mm)')),
                ('total_length', models.FloatField(blank=True, null=True, verbose_name='total length (mm)')),
                ('weight', models.FloatField(blank=True, null=True, verbose_name='weight (g)')),
                ('tag_number', models.CharField(blank=True, max_length=12, null=True, verbose_name='tag number')),
                ('scale_id_number', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='scale ID number')),
                ('age_type', models.IntegerField(blank=True, choices=[(1, 'scale'), (2, 'length-frequency')], null=True, verbose_name='age type')),
                ('river_age', models.IntegerField(blank=True, null=True, verbose_name='river age')),
                ('notes', models.TextField(blank=True, null=True)),
                ('old_id', models.CharField(blank=True, editable=False, max_length=25, null=True)),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='biologicaldetail_created_by', to=settings.AUTH_USER_MODEL)),
                ('maturity', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='biological_detailings', to='trapnet.maturity')),
                ('reproductive_status', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='biological_detailings', to='trapnet.reproductivestatus')),
                ('sample', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='biological_detailings', to='trapnet.sample')),
                ('sex', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='biological_detailings', to='trapnet.sex')),
                ('species', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='biological_detailings', to='trapnet.species')),
                ('status', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='biological_detailings', to='trapnet.status')),
                ('updated_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='biologicaldetail_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['sample__arrival_date'],
            },
        ),
    ]
