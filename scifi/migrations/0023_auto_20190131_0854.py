# Generated by Django 2.1.4 on 2019-01-31 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scifi', '0022_auto_20190131_0842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_lead',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
