# Generated by Django 3.2.14 on 2022-12-02 20:11

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('trapnet', '0008_sample_age_thresh_parr_smolt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sample',
            name='didymo',
            field=models.IntegerField(blank=True, choices=[(None, 'No data'), (0, 'Absent'), (1, 'Present')], null=True, verbose_name='presence / absence of Didymosphenia geminata'),
        ),
        migrations.CreateModel(
            name='TrapnetSample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('water_temp_trap_c', models.FloatField(blank=True, null=True, verbose_name='water temperature at trap (°C)')),
                ('time_released', models.DateTimeField(blank=True, null=True, verbose_name='time released')),
                ('samplers', models.TextField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='trapnetsample_created_by', to=settings.AUTH_USER_MODEL)),
                ('sample', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='trapnet_sample', to='trapnet.sample')),
                ('updated_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='trapnetsample_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RSTSample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('water_temp_trap_c', models.FloatField(blank=True, null=True, verbose_name='water temperature at trap (°C)')),
                ('water_depth_m', models.FloatField(blank=True, null=True, verbose_name='water depth (m)')),
                ('water_level_delta_m', models.FloatField(blank=True, null=True, verbose_name='water level delta (m)')),
                ('discharge_m3_sec', models.FloatField(blank=True, null=True, verbose_name='discharge (m3/s)')),
                ('rpm_arrival', models.FloatField(blank=True, null=True, verbose_name='RPM at start')),
                ('rpm_departure', models.FloatField(blank=True, null=True, verbose_name='RPM at end')),
                ('time_released', models.DateTimeField(blank=True, null=True, verbose_name='time released')),
                ('operating_condition', models.IntegerField(blank=True, choices=[(1, 'fully operational'), (2, 'partially operational'), (3, 'not operational')], null=True)),
                ('operating_condition_comment', models.CharField(blank=True, max_length=255, null=True)),
                ('samplers', models.TextField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='rstsample_created_by', to=settings.AUTH_USER_MODEL)),
                ('sample', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='rst_sample', to='trapnet.sample')),
                ('updated_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='rstsample_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EFSample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('site_type', models.IntegerField(blank=True, choices=[(1, 'Open'), (2, 'Closed')], null=True, verbose_name='type of site')),
                ('seine_type', models.IntegerField(blank=True, choices=[(1, '1 man seine (1m wide X 1m high)'), (2, '2 man lip seine (3m wide X 1m high)')], default=2, null=True, verbose_name='type of seine')),
                ('percent_riffle', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='riffle')),
                ('percent_run', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='run')),
                ('percent_flat', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='flat')),
                ('percent_pool', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='pool')),
                ('bank_length_left', models.FloatField(blank=True, null=True, verbose_name='bank length - left (m)')),
                ('overhanging_veg_left', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='Overhanging Vegetation (%) - Left')),
                ('max_overhanging_veg_left', models.FloatField(blank=True, null=True, verbose_name='Max Overhanging Vegetation (m) - Left')),
                ('bank_length_right', models.FloatField(blank=True, null=True, verbose_name='bank length - right (m)')),
                ('overhanging_veg_right', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='Overhanging Vegetation (%) - Right')),
                ('max_overhanging_veg_right', models.FloatField(blank=True, null=True, verbose_name='Max Overhanging Vegetation (m) - Right')),
                ('didymo', models.IntegerField(blank=True, choices=[(None, 'No data'), (0, 'Absent'), (1, 'Present')], null=True, verbose_name='presence / absence of Didymosphenia geminata')),
                ('width_lower', models.FloatField(blank=True, null=True, verbose_name='width - lower (m)')),
                ('depth_1_lower', models.FloatField(blank=True, null=True, verbose_name='depth #1 - lower (cm)')),
                ('depth_2_lower', models.FloatField(blank=True, null=True, verbose_name='depth #2 - lower (cm)')),
                ('depth_3_lower', models.FloatField(blank=True, null=True, verbose_name='depth #3 - lower (cm)')),
                ('width_middle', models.FloatField(blank=True, null=True, verbose_name='width - middle (m)')),
                ('depth_1_middle', models.FloatField(blank=True, null=True, verbose_name='depth #1 - middle (cm)')),
                ('depth_2_middle', models.FloatField(blank=True, null=True, verbose_name='depth #2 - middle (cm)')),
                ('depth_3_middle', models.FloatField(blank=True, null=True, verbose_name='depth #3 - middle (cm)')),
                ('width_upper', models.FloatField(blank=True, null=True, verbose_name='width - upper (m)')),
                ('depth_1_upper', models.FloatField(blank=True, null=True, verbose_name='depth #1 - upper (cm)')),
                ('depth_2_upper', models.FloatField(blank=True, null=True, verbose_name='depth #2 - upper (cm)')),
                ('depth_3_upper', models.FloatField(blank=True, null=True, verbose_name='depth #3 - upper (cm)')),
                ('max_depth', models.FloatField(blank=True, help_text='max depth found within the whole site', null=True, verbose_name='max depth (cm)')),
                ('water_cond', models.FloatField(blank=True, help_text='The measurement is to 1 decimal place in micro siemens (µS)', null=True, verbose_name='specific conductivity (µS)')),
                ('water_ph', models.FloatField(blank=True, null=True, verbose_name='water acidity (pH)')),
                ('percent_fine', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='fine silt or clay')),
                ('percent_sand', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='sand')),
                ('percent_gravel', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='gravel')),
                ('percent_pebble', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='pebble')),
                ('percent_cobble', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='cobble')),
                ('percent_rocks', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='rocks')),
                ('percent_boulder', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='boulder')),
                ('percent_bedrock', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='bedrock')),
                ('electrofisher_voltage', models.FloatField(blank=True, null=True, verbose_name='electrofisher voltage (V)')),
                ('electrofisher_output_low', models.FloatField(blank=True, null=True, verbose_name='electrofisher output, low (amps)')),
                ('electrofisher_output_high', models.FloatField(blank=True, null=True, verbose_name='electrofisher output, high (amps)')),
                ('electrofisher_frequency', models.FloatField(blank=True, null=True, verbose_name='electrofisher frequency (Hz)')),
                ('electrofisher_pulse_type', models.IntegerField(blank=True, choices=[(1, 'Standard pulse '), (2, 'Direct current'), (3, 'Burst of pulses')], null=True, verbose_name='type of pulse')),
                ('duty_cycle', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='duty cycle (%)')),
                ('crew_probe', models.CharField(blank=True, max_length=255, null=True, verbose_name='crew (probe)')),
                ('crew_seine', models.CharField(blank=True, max_length=255, null=True, verbose_name='crew (seine)')),
                ('crew_dipnet', models.CharField(blank=True, max_length=255, null=True, verbose_name='crew (dipnet)')),
                ('crew_extras', models.CharField(blank=True, max_length=255, null=True, verbose_name='crew (extras)')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='efsample_created_by', to=settings.AUTH_USER_MODEL)),
                ('electrofisher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='ef_samples', to='trapnet.electrofisher', verbose_name='electrofisher')),
                ('sample', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ef_sample', to='trapnet.sample')),
                ('updated_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='efsample_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
