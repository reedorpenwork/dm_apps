# Generated by Django 3.2.4 on 2021-10-08 00:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20210511_1253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='announcement',
            name='subject_en',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
