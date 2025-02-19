# Generated by Django 3.2.12 on 2022-05-10 11:45

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('masterlist', '0012_alter_person_designation'),
        ('maret', '0018_auto_20220502_0833'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='committee',
            name='external_chair',
        ),
        migrations.AddField(
            model_name='committee',
            name='external_chair',
            field=models.ManyToManyField(blank=True, to='masterlist.Person', verbose_name='External Chair'),
        ),
        migrations.AlterField(
            model_name='interaction',
            name='date_of_meeting',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='Date of Interaction'),
        ),
    ]
