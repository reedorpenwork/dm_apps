# Generated by Django 3.2.4 on 2021-10-07 14:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shared_models', '0024_person_expertise'),
    ]

    operations = [
        migrations.AddField(
            model_name='cruise',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cruise',
            name='created_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='cruise_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cruise',
            name='editors',
            field=models.ManyToManyField(blank=True, help_text='A list of dmapps user who can edit this cruise', related_name='cruise_editors', to=settings.AUTH_USER_MODEL, verbose_name='editors'),
        ),
        migrations.AddField(
            model_name='cruise',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='cruise',
            name='updated_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='cruise_updated_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
