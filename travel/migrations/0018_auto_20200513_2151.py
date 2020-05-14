# Generated by Django 2.2.2 on 2020-05-14 00:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0017_auto_20200513_2146'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='trippurpose',
            options={'ordering': ['name']},
        ),
        migrations.RemoveField(
            model_name='trippurpose',
            name='description_en',
        ),
        migrations.RemoveField(
            model_name='trippurpose',
            name='description_fr',
        ),
        migrations.CreateModel(
            name='TripSubPurpose',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('nom', models.CharField(blank=True, max_length=255, null=True)),
                ('description_en', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('description_fr', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('trip_purpose', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='sub_purposes', to='travel.TripPurpose')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
