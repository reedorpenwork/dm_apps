# Generated by Django 3.2.12 on 2022-03-22 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fisheriescape', '0032_add_metadata_shared_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='nafoarea',
            name='layer_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='layer id'),
        ),
    ]
