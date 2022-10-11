# Generated by Django 3.2.14 on 2022-08-19 18:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tracking', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_email', models.TextField(blank=True, null=True)),
                ('recipient_list', models.TextField(blank=True, null=True)),
                ('subject_en', models.TextField(blank=True, null=True)),
                ('subject_fr', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('sent_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='email_sent_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
