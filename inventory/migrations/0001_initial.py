# Generated by Django 2.1.4 on 2019-03-14 19:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import inventory.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='BoundingBox',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('west_bounding', models.FloatField(blank=True, null=True)),
                ('south_bounding', models.FloatField(blank=True, null=True)),
                ('east_bounding', models.FloatField(blank=True, null=True)),
                ('north_bounding', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CharacterSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=25)),
                ('code', models.CharField(blank=True, max_length=25, null=True)),
                ('notes', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Citation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title_eng', models.TextField(blank=True, null=True, verbose_name='Title (English)')),
                ('title_fre', models.TextField(blank=True, null=True, verbose_name='Title (French)')),
                ('authors', models.TextField(blank=True, null=True)),
                ('year', models.IntegerField(blank=True, null=True)),
                ('pub_number', models.CharField(blank=True, max_length=255, null=True, verbose_name='Publication Number')),
                ('url_eng', models.TextField(blank=True, null=True, verbose_name='URL (English)')),
                ('url_fre', models.TextField(blank=True, null=True, verbose_name='URL (French)')),
                ('abstract_eng', models.TextField(blank=True, null=True, verbose_name='Abstrast (English)')),
                ('abstract_fre', models.TextField(blank=True, null=True, verbose_name='Abstrast (French)')),
                ('series', models.CharField(blank=True, max_length=1000, null=True)),
                ('region', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ContentType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Name (English)')),
                ('english_value', models.CharField(max_length=255, verbose_name='Name (French)')),
                ('french_value', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Correspondence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255)),
                ('date', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='DataResource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('name_eng', models.CharField(max_length=255, verbose_name='Name (English)')),
                ('name_fre', models.CharField(max_length=255, verbose_name='Name (French)')),
                ('protocol', models.CharField(choices=[('HTTP', 'HTTP'), ('HTTPS', 'HTTPS'), ('FTP', 'FTP')], max_length=255)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('caption', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to=inventory.models.file_directory_path)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['-date_created'],
            },
        ),
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_value_eng', models.CharField(blank=True, max_length=1000, null=True, verbose_name='Keyword value (English)')),
                ('text_value_fre', models.CharField(blank=True, max_length=1000, null=True, verbose_name='Keyword value (French)')),
                ('uid', models.CharField(blank=True, max_length=1000, null=True, verbose_name='Unique Identifier')),
                ('concept_scheme', models.CharField(blank=True, max_length=1000, null=True)),
                ('details', models.TextField(blank=True, null=True)),
                ('xml_block', models.TextField(blank=True, null=True)),
                ('is_taxonomic', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['keyword_domain', 'text_value_eng'],
            },
        ),
        migrations.CreateModel(
            name='KeywordDomain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_eng', models.CharField(blank=True, max_length=255, null=True)),
                ('name_fre', models.CharField(blank=True, max_length=255, null=True)),
                ('abbrev', models.CharField(blank=True, max_length=255, null=True)),
                ('url', models.URLField(blank=True, null=True)),
                ('web_services', models.BooleanField()),
                ('xml_block', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location_eng', models.CharField(blank=True, max_length=1000, null=True)),
                ('location_fre', models.CharField(blank=True, max_length=1000, null=True)),
                ('country', models.CharField(choices=[('Canada', 'Canada'), ('United States', 'United States')], max_length=25)),
                ('abbrev_eng', models.CharField(blank=True, max_length=25, null=True)),
                ('abbrev_fre', models.CharField(blank=True, max_length=25, null=True)),
                ('uuid_gcmd', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Maintenance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('frequency', models.CharField(max_length=25)),
                ('code', models.CharField(blank=True, max_length=25, null=True)),
                ('notes', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_eng', models.CharField(blank=True, max_length=1000, null=True)),
                ('name_fre', models.CharField(blank=True, max_length=1000, null=True)),
                ('abbrev', models.CharField(blank=True, max_length=255, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('city', models.CharField(blank=True, max_length=255, null=True)),
                ('postal_code', models.CharField(blank=True, max_length=7, null=True)),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='inventory.Location')),
            ],
            options={
                'ordering': ['name_eng'],
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='person', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('full_name', models.CharField(blank=True, max_length=255, null=True)),
                ('position_eng', models.CharField(blank=True, max_length=255, null=True)),
                ('position_fre', models.CharField(blank=True, max_length=255, null=True)),
                ('phone', models.CharField(blank=True, max_length=25, null=True)),
                ('language', models.IntegerField(blank=True, choices=[(1, 'English'), (2, 'French')], null=True, verbose_name='language preference')),
                ('organization', models.ForeignKey(blank=True, default=6, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='inventory.Organization')),
            ],
            options={
                'ordering': ['user__last_name', 'user__first_name'],
            },
        ),
        migrations.CreateModel(
            name='PersonRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(max_length=25)),
                ('code', models.CharField(blank=True, max_length=25, null=True)),
                ('notes', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1000)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(blank=True, null=True, verbose_name='UUID')),
                ('title_eng', models.TextField(verbose_name='Title (English)')),
                ('title_fre', models.TextField(blank=True, null=True, verbose_name='Title (French)')),
                ('purpose_eng', models.TextField(blank=True, null=True, verbose_name='Purpose (English)')),
                ('purpose_fre', models.TextField(blank=True, null=True, verbose_name='Purpose (French)')),
                ('descr_eng', models.TextField(blank=True, null=True, verbose_name='Description (English)')),
                ('descr_fre', models.TextField(blank=True, null=True, verbose_name='Description (French)')),
                ('time_start_day', models.IntegerField(blank=True, null=True, verbose_name='Start day')),
                ('time_start_month', models.IntegerField(blank=True, null=True, verbose_name='Start month')),
                ('time_start_year', models.IntegerField(blank=True, null=True, verbose_name='Start year')),
                ('time_end_day', models.IntegerField(blank=True, null=True, verbose_name='End day')),
                ('time_end_month', models.IntegerField(blank=True, null=True, verbose_name='End month')),
                ('time_end_year', models.IntegerField(blank=True, null=True, verbose_name='End year')),
                ('sampling_method_eng', models.TextField(blank=True, null=True, verbose_name='Sampling method (English)')),
                ('sampling_method_fre', models.TextField(blank=True, null=True, verbose_name='Sampling method (French)')),
                ('physical_sample_descr_eng', models.TextField(blank=True, null=True, verbose_name='Description of physical samples (English)')),
                ('physical_sample_descr_fre', models.TextField(blank=True, null=True, verbose_name='Description of physical samples (French)')),
                ('resource_constraint_eng', models.TextField(blank=True, null=True, verbose_name='Resource constraint (English)')),
                ('resource_constraint_fre', models.TextField(blank=True, null=True, verbose_name='Resource constraint (French)')),
                ('qc_process_descr_eng', models.TextField(blank=True, null=True, verbose_name='QC process description (English)')),
                ('qc_process_descr_fre', models.TextField(blank=True, null=True, verbose_name='QC process description (French)')),
                ('security_use_limitation_eng', models.CharField(blank=True, max_length=255, null=True, verbose_name='Security use limitation (English)')),
                ('security_use_limitation_fre', models.CharField(blank=True, max_length=255, null=True, verbose_name='Security use limitation (French)')),
                ('storage_envr_notes', models.TextField(blank=True, null=True, verbose_name='Storage notes (internal)')),
                ('distribution_format', models.CharField(blank=True, choices=[('AAC', 'AAC'), ('AI', 'AI'), ('AIFF', 'AIFF'), ('AMF', 'AMF'), ('ASCII Grid', 'ASCII Grid'), ('AVI', 'AVI'), ('Android', 'Android'), ('BMP', 'BMP'), ('BWF', 'BWF'), ('Blackberry', 'Blackberry'), ('CCT', 'CCT'), ('CDED ASCII', 'CDED ASCII'), ('CDF', 'CDF'), ('CDR', 'CDR'), ('CSV', 'CSV'), ('DBD', 'DBD'), ('DBF', 'DBF'), ('DICOM', 'DICOM'), ('DNG', 'DNG'), ('DOC', 'DOC'), ('DOCX', 'DOCX'), ('DXF', 'DXF'), ('E00', 'E00'), ('ECW', 'ECW'), ('EDI', 'EDI'), ('EMF', 'EMF'), ('EPS', 'EPS'), ('EPUB2', 'EPUB2'), ('EPUB3', 'EPUB3'), ('ESRI REST', 'ESRI REST'), ('EXE', 'EXE'), ('FGDB/GDB', 'FGDB/GDB'), ('Flat raster binary', 'Flat raster binary'), ('GIF', 'GIF'), ('GML', 'GML'), ('GRIB1', 'GRIB1'), ('GRIB2', 'GRIB2'), ('GeoJSON', 'GeoJSON'), ('GeoPDF', 'GeoPDF'), ('GeoPackage', 'GeoPackage'), ('GeoRSS', 'GeoRSS'), ('GeoTIF', 'GeoTIF'), ('HDF', 'HDF'), ('HTML', 'HTML'), ('IATI', 'IATI'), ('IOS', 'IOS'), ('JAR', 'JAR'), ('JFIF', 'JFIF'), ('JPEG 2000', 'JPEG 2000'), ('JPEG2', 'JPEG2'), ('JPG', 'JPG'), ('JSON', 'JSON'), ('JSON Lines', 'JSON Lines'), ('JSON-LD', 'JSON-LD'), ('KML', 'KML'), ('KMZ', 'KMZ'), ('LAS', 'LAS'), ('LYR', 'LYR'), ('MOV', 'MOV'), ('MP3', 'MP3'), ('MPEG', 'MPEG'), ('MPEG-1', 'MPEG-1'), ('MXD', 'MXD'), ('MXF', 'MXF'), ('MapInfo', 'MapInfo'), ('NetCDF', 'NetCDF'), ('ODP', 'ODP'), ('ODS', 'ODS'), ('ODT', 'ODT'), ('PDF', 'PDF'), ('PDF/A-1', 'PDF/A-1'), ('PDF/A-2', 'PDF/A-2'), ('PNG', 'PNG'), ('PPT', 'PPT'), ('RDF', 'RDF'), ('RDF Turtle', 'RDF Turtle'), ('RDF n-triples', 'RDF n-triples'), ('RDF/XML', 'RDF/XML'), ('RDFa', 'RDFa'), ('RSS', 'RSS'), ('SAR', 'SAR'), ('SAV', 'SAV'), ('SEGY', 'SEGY'), ('SHP', 'SHP'), ('SQL', 'SQL'), ('SQL Lite', 'SQL Lite'), ('SVG', 'SVG'), ('TAB', 'TAB'), ('TIFF', 'TIFF'), ('TRiG', 'TRiG'), ('TRiX', 'TRiX'), ('TXT', 'TXT'), ('VPF', 'VPF'), ('WAV', 'WAV'), ('WFS', 'WFS'), ('WMS', 'WMS'), ('WMTS', 'WMTS'), ('WMV', 'WMV'), ('WPS', 'WPS'), ('Web App', 'Web App'), ('XLS', 'XLS'), ('XLSM', 'XLSM'), ('XML', 'XML'), ('ZIP', 'ZIP')], max_length=255, null=True)),
                ('geo_descr_eng', models.CharField(blank=True, max_length=255, null=True, verbose_name='Geographic description (English)')),
                ('geo_descr_fre', models.CharField(blank=True, max_length=255, null=True, verbose_name='Geographic description (French)')),
                ('west_bounding', models.FloatField(blank=True, null=True, verbose_name='West bounding coordinate')),
                ('south_bounding', models.FloatField(blank=True, null=True, verbose_name='South bounding coordinate')),
                ('east_bounding', models.FloatField(blank=True, null=True, verbose_name='East bounding coordinate')),
                ('north_bounding', models.FloatField(blank=True, null=True, verbose_name='North bounding coordinate')),
                ('parameters_collected_eng', models.TextField(blank=True, null=True, verbose_name='Parameters collected (English)')),
                ('parameters_collected_fre', models.TextField(blank=True, null=True, verbose_name='Parameters collected (French)')),
                ('additional_credit', models.TextField(blank=True, null=True)),
                ('analytic_software', models.TextField(blank=True, null=True, verbose_name='Analytic software notes (internal)')),
                ('date_verified', models.DateTimeField(blank=True, null=True)),
                ('fgp_publication_date', models.DateTimeField(blank=True, null=True, verbose_name='Date published to FGP')),
                ('open_data_notes', models.CharField(blank=True, max_length=255, null=True, verbose_name='Open data notes (internal only)')),
                ('public_url', models.CharField(blank=True, max_length=1000, null=True, verbose_name='Public URL')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='General notes (internal)')),
                ('date_last_modified', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
                ('flagged_4_deletion', models.BooleanField(default=False)),
                ('flagged_4_publication', models.BooleanField(default=False)),
                ('completedness_report', models.TextField(blank=True, null=True, verbose_name='completedness report')),
                ('completedness_rating', models.FloatField(blank=True, null=True, verbose_name='completedness rating')),
                ('translation_needed', models.BooleanField(default=True, verbose_name='translation needed')),
                ('citations', models.ManyToManyField(related_name='resources', to='inventory.Citation')),
                ('data_char_set', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='inventory.CharacterSet', verbose_name='Data character set')),
                ('keywords', models.ManyToManyField(related_name='resources', to='inventory.Keyword')),
                ('last_modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('maintenance', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='inventory.Maintenance', verbose_name='Maintenance frequency')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='children', to='inventory.Resource', verbose_name='Parent resource')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='ResourceCertification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('certification_date', models.DateTimeField(blank=True, null=True, verbose_name='Date published to FGP')),
                ('notes', models.TextField(blank=True, null=True)),
                ('certifying_user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('resource', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='certification_history', to='inventory.Resource')),
            ],
            options={
                'db_table': 'inventory_resource_certification',
                'ordering': ['-certification_date'],
            },
        ),
        migrations.CreateModel(
            name='ResourcePerson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notes', models.TextField(blank=True, null=True)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='resource_people', to='inventory.Person')),
                ('resource', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='resource_people', to='inventory.Resource')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='inventory.PersonRole')),
            ],
            options={
                'db_table': 'inventory_resource_people',
                'ordering': ['role'],
            },
        ),
        migrations.CreateModel(
            name='ResourceType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=25)),
                ('code', models.CharField(blank=True, max_length=25, null=True)),
            ],
            options={
                'db_table': 'inventory_resource_type',
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section', models.CharField(max_length=255)),
                ('abbrev', models.CharField(blank=True, max_length=25, null=True)),
                ('division', models.CharField(blank=True, max_length=255, null=True)),
                ('branch', models.CharField(blank=True, max_length=255, null=True)),
                ('region', models.IntegerField(choices=[(1, 'Gulf'), (2, 'Maritime'), (3, 'Quebec'), (4, 'Central & Arctic'), (5, 'Pacific'), (6, 'Newfoundland and Labrador')])),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='section_manangers', to='inventory.Person')),
                ('unit_head', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='section_heads', to='inventory.Person')),
            ],
            options={
                'ordering': ['section'],
            },
        ),
        migrations.CreateModel(
            name='SecurityClassification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=25)),
                ('code', models.CharField(blank=True, max_length=25, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SpatialReferenceSystem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255)),
                ('code', models.CharField(blank=True, max_length=25, null=True)),
                ('codespace', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SpatialRepresentationType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=25)),
                ('code', models.CharField(blank=True, max_length=25, null=True)),
                ('notes', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=25)),
                ('code', models.CharField(blank=True, max_length=25, null=True)),
                ('notes', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='WebService',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('protocol', models.CharField(default='ESRI REST: Map Service', max_length=255)),
                ('service_language', models.CharField(choices=[('urn:xml:lang:eng-CAN', 'English'), ('urn:xml:lang:fra-CAN', 'French')], max_length=255)),
                ('url', models.URLField()),
                ('name_eng', models.CharField(max_length=255, verbose_name='Name (English)')),
                ('name_fre', models.CharField(max_length=255, verbose_name='Name (French)')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.ContentType')),
                ('resource', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='web_services', to='inventory.Resource')),
            ],
        ),
        migrations.AddField(
            model_name='resource',
            name='people',
            field=models.ManyToManyField(through='inventory.ResourcePerson', to='inventory.Person'),
        ),
        migrations.AddField(
            model_name='resource',
            name='resource_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='inventory.ResourceType'),
        ),
        migrations.AddField(
            model_name='resource',
            name='section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='resources', to='inventory.Section'),
        ),
        migrations.AddField(
            model_name='resource',
            name='security_classification',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='inventory.SecurityClassification'),
        ),
        migrations.AddField(
            model_name='resource',
            name='spat_ref_system',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='inventory.SpatialReferenceSystem', verbose_name='Spatial reference system'),
        ),
        migrations.AddField(
            model_name='resource',
            name='spat_representation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='inventory.SpatialRepresentationType', verbose_name='Spatial representation type'),
        ),
        migrations.AddField(
            model_name='resource',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='inventory.Status'),
        ),
        migrations.AddField(
            model_name='keyword',
            name='keyword_domain',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='inventory.KeywordDomain'),
        ),
        migrations.AddField(
            model_name='file',
            name='resource',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='inventory.Resource'),
        ),
        migrations.AddField(
            model_name='dataresource',
            name='resource',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data_resources', to='inventory.Resource'),
        ),
        migrations.AddField(
            model_name='correspondence',
            name='custodian',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='correspondences', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='citation',
            name='publication',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='inventory.Publication'),
        ),
        migrations.AlterUniqueTogether(
            name='resourceperson',
            unique_together={('resource', 'person', 'role')},
        ),
    ]
