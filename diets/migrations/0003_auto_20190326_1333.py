# Generated by Django 2.1.4 on 2019-03-26 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diets', '0002_auto_20190326_1328'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prey',
            name='length_is_approximation',
        ),
        migrations.AddField(
            model_name='prey',
            name='length_comment',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
