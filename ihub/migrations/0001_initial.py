# Generated by Django 3.1.2 on 2021-01-25 12:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import ihub.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shared_models', '0001_initial'),
        ('masterlist', '0009_auto_20201218_1111'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=1000, null=True, verbose_name='title')),
                ('location', models.CharField(blank=True, max_length=1000, null=True, verbose_name='location')),
                ('proponent', models.CharField(blank=True, max_length=1000, null=True, verbose_name='proponent')),
                ('initial_date', models.DateTimeField(blank=True, null=True, verbose_name='initial activity date')),
                ('anticipated_end_date', models.DateTimeField(blank=True, null=True, verbose_name='anticipated end date')),
                ('fiscal_year', models.CharField(blank=True, max_length=1000, null=True, verbose_name='fiscal year/multiyear')),
                ('funding_needed', models.IntegerField(blank=True, choices=[(None, '---------'), (1, 'Yes'), (0, 'No')], null=True, verbose_name='is funding needed?')),
                ('amount_requested', models.FloatField(blank=True, null=True, verbose_name='funding requested')),
                ('amount_approved', models.FloatField(blank=True, null=True, verbose_name='funding approved')),
                ('amount_transferred', models.FloatField(blank=True, null=True, verbose_name='amount transferred')),
                ('amount_lapsed', models.FloatField(blank=True, null=True, verbose_name='amount lapsed')),
                ('amount_owing', models.IntegerField(blank=True, choices=[(None, '---------'), (1, 'Yes'), (0, 'No')], null=True, verbose_name='does any funding need to be recovered?')),
                ('date_last_modified', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='date last modified')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date created')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_entries', to=settings.AUTH_USER_MODEL, verbose_name='created by')),
            ],
            options={
                'ordering': ['-date_created'],
            },
        ),
        migrations.CreateModel(
            name='EntryType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='name (en)')),
                ('nom', models.CharField(blank=True, max_length=255, null=True, verbose_name='name (fr)')),
                ('color', models.CharField(blank=True, max_length=25, null=True)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FundingProgram',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='name (en)')),
                ('nom', models.CharField(blank=True, max_length=255, null=True, verbose_name='name (fr)')),
                ('abbrev_eng', models.CharField(blank=True, max_length=255, null=True, verbose_name='abbreviation (French)')),
                ('abbrev_fre', models.CharField(blank=True, max_length=255, null=True, verbose_name='abbreviation (French)')),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FundingPurpose',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='name (en)')),
                ('nom', models.CharField(blank=True, max_length=255, null=True, verbose_name='name (fr)')),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='name (en)')),
                ('nom', models.CharField(blank=True, max_length=255, null=True, verbose_name='name (fr)')),
                ('color', models.CharField(blank=True, max_length=25, null=True)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('caption', models.CharField(max_length=255, verbose_name='caption')),
                ('file', models.FileField(upload_to=ihub.models.file_directory_path, verbose_name='file')),
                ('date_uploaded', models.DateTimeField(auto_now=True, verbose_name='date uploaded')),
                ('entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='ihub.entry')),
            ],
            options={
                'ordering': ['-date_uploaded'],
            },
        ),
        migrations.CreateModel(
            name='EntryPerson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='name')),
                ('organization', models.CharField(max_length=50)),
                ('role', models.IntegerField(blank=True, choices=[(1, 'Lead'), (2, 'Contact'), (3, 'Support')], null=True, verbose_name='role')),
                ('entry', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='people', to='ihub.entry')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='ihub_entry_people', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'ordering': ['role', 'user__first_name', 'user__last_name'],
            },
        ),
        migrations.CreateModel(
            name='EntryNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField(choices=[(1, 'Action'), (2, 'Next step'), (3, 'Comment'), (4, 'Follow-up (*)'), (5, 'Internal')])),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('note', models.TextField()),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='author')),
                ('entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='ihub.entry')),
                ('status', models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='entry_notes', to='ihub.status', verbose_name='status')),
            ],
            options={
                'ordering': ['-creation_date'],
            },
        ),
        migrations.AddField(
            model_name='entry',
            name='entry_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='entries', to='ihub.entrytype', verbose_name='Entry Type'),
        ),
        migrations.AddField(
            model_name='entry',
            name='funding_program',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='entries', to='ihub.fundingprogram', verbose_name='funding program'),
        ),
        migrations.AddField(
            model_name='entry',
            name='funding_purpose',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='entries', to='ihub.fundingpurpose', verbose_name='funding purpose'),
        ),
        migrations.AddField(
            model_name='entry',
            name='last_modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='last modified by'),
        ),
        migrations.AddField(
            model_name='entry',
            name='organizations',
            field=models.ManyToManyField(limit_choices_to={'grouping__is_indigenous': True}, related_name='entries', to='masterlist.Organization'),
        ),
        migrations.AddField(
            model_name='entry',
            name='regions',
            field=models.ManyToManyField(related_name='entries', to='shared_models.Region'),
        ),
        migrations.AddField(
            model_name='entry',
            name='sectors',
            field=models.ManyToManyField(related_name='entries', to='masterlist.Sector', verbose_name='DFO sectors'),
        ),
        migrations.AddField(
            model_name='entry',
            name='status',
            field=models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='entries', to='ihub.status', verbose_name='status'),
        ),
    ]
