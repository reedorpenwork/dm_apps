# Generated by Django 3.1.2 on 2020-12-23 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('whalesdb', '0008_helptext'),
    ]

    operations = [
        migrations.AddField(
            model_name='helptext',
            name='model',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
