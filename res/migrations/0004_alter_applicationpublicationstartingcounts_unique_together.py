# Generated by Django 3.2.14 on 2022-12-08 12:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('res', '0003_applicationpublicationstartingcounts'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='applicationpublicationstartingcounts',
            unique_together={('application', 'publication_type')},
        ),
    ]
