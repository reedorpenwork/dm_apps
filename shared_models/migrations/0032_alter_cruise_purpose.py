# Generated by Django 3.2.14 on 2022-10-04 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shared_models', '0031_subjectmatter_is_csas_request_tag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cruise',
            name='purpose',
            field=models.TextField(blank=True, null=True, verbose_name='Purpose'),
        ),
    ]
