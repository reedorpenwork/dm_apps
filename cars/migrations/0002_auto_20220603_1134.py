# Generated by Django 3.2.13 on 2022-06-03 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='location',
            options={'ordering': ['name']},
        ),
        migrations.AddField(
            model_name='location',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='reference_number',
            field=models.CharField(max_length=50, verbose_name='reference number'),
        ),
    ]
