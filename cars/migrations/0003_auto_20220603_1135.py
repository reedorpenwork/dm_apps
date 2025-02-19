# Generated by Django 3.2.13 on 2022-06-03 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0002_auto_20220603_1134'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='nom',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='name (fr)'),
        ),
        migrations.AlterField(
            model_name='location',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='name (en)'),
        ),
    ]
