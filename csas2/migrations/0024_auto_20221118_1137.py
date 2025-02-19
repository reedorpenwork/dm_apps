# Generated by Django 3.2.14 on 2022-11-18 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csas2', '0023_rename_pages_document_pages_en'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='pdf_size_kb_en',
            field=models.IntegerField(blank=True, null=True, verbose_name='size of PDF (en)'),
        ),
        migrations.AddField(
            model_name='document',
            name='pdf_size_kb_fr',
            field=models.IntegerField(blank=True, null=True, verbose_name='size of PDF (fr)'),
        ),
    ]
