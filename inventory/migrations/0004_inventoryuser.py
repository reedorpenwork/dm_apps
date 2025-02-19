# Generated by Django 3.2.10 on 2022-04-21 15:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shared_models', '0031_subjectmatter_is_csas_request_tag'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inventory', '0003_resource_thumbnail_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='InventoryUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_admin', models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False, verbose_name='national administrator?')),
                ('region', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inventory_users', to='shared_models.region', verbose_name='regional administrator?')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='inventory_user', to=settings.AUTH_USER_MODEL, verbose_name='DM Apps user')),
            ],
            options={
                'ordering': ['-is_admin', 'user__first_name'],
            },
        ),
    ]
