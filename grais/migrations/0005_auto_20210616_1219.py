# Generated by Django 3.2.2 on 2021-06-16 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grais', '0004_bait'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bait',
            name='nom',
        ),
        migrations.AlterField(
            model_name='bait',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='name'),
        ),
    ]
