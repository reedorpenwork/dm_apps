# Generated by Django 3.2.15 on 2022-12-20 15:41

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('whalebrary', '0012_alter_maintenance_maint_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='quantity',
            field=models.FloatField(default=1, validators=[django.core.validators.MinValueValidator(1)], verbose_name='quantity'),
            preserve_default=False,
        ),
    ]
