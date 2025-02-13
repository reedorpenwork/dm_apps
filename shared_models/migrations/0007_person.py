# Generated by Django 3.2 on 2021-04-16 11:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shared_models', '0006_auto_20210225_1538'),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='last name')),
                ('phone', models.CharField(blank=True, max_length=100, null=True, verbose_name='phone')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email')),
                ('affiliation', models.CharField(blank=True, max_length=255, null=True, verbose_name='affiliation')),
                ('job_title_en', models.CharField(blank=True, max_length=100, null=True, verbose_name='Job Title')),
                ('job_title_fr', models.CharField(blank=True, max_length=100, null=True, verbose_name='Job Title')),
                ('type', models.IntegerField(blank=True, null=True, verbose_name='Type')),
                ('notification_preference', models.IntegerField(blank=True, null=True, verbose_name='Communication Preference')),
                ('expertise', models.IntegerField(blank=True, null=True, verbose_name='Expertise')),
                ('cc_grad', models.BooleanField(blank=True, null=True, verbose_name='Chair Course Graduate')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('old_id', models.IntegerField(blank=True, editable=False, null=True)),
                ('dmapps_user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='people', to=settings.AUTH_USER_MODEL, verbose_name='linkage to DM Apps User')),
                ('language', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='people', to='shared_models.language', verbose_name='language preference')),
            ],
            options={
                'ordering': ['first_name', 'last_name'],
            },
        ),
    ]
