# Generated by Django 2.2.2 on 2020-05-20 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0026_auto_20200514_1610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cost',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='name (en)'),
        ),
        migrations.AlterField(
            model_name='cost',
            name='nom',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='name (fr)'),
        ),
        migrations.AlterField(
            model_name='costcategory',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='name (en)'),
        ),
        migrations.AlterField(
            model_name='costcategory',
            name='nom',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='name (fr)'),
        ),
        migrations.AlterField(
            model_name='njcrates',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='name (en)'),
        ),
        migrations.AlterField(
            model_name='njcrates',
            name='nom',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='name (fr)'),
        ),
        migrations.AlterField(
            model_name='purpose',
            name='description_en',
            field=models.TextField(blank=True, null=True, verbose_name='Description (en)'),
        ),
        migrations.AlterField(
            model_name='purpose',
            name='description_fr',
            field=models.TextField(blank=True, null=True, verbose_name='Description (fr)'),
        ),
        migrations.AlterField(
            model_name='purpose',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='name (en)'),
        ),
        migrations.AlterField(
            model_name='purpose',
            name='nom',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='name (fr)'),
        ),
        migrations.AlterField(
            model_name='reason',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='name (en)'),
        ),
        migrations.AlterField(
            model_name='reason',
            name='nom',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='name (fr)'),
        ),
        migrations.AlterField(
            model_name='reviewerrole',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='name (en)'),
        ),
        migrations.AlterField(
            model_name='reviewerrole',
            name='nom',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='name (fr)'),
        ),
        migrations.AlterField(
            model_name='role',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='name (en)'),
        ),
        migrations.AlterField(
            model_name='role',
            name='nom',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='name (fr)'),
        ),
        migrations.AlterField(
            model_name='status',
            name='nom',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='name (fr)'),
        ),
        migrations.AlterField(
            model_name='tripcategory',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='name (en)'),
        ),
        migrations.AlterField(
            model_name='tripcategory',
            name='nom',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='name (fr)'),
        ),
        migrations.AlterField(
            model_name='tripsubcategory',
            name='description_en',
            field=models.TextField(blank=True, null=True, verbose_name='Description (en)'),
        ),
        migrations.AlterField(
            model_name='tripsubcategory',
            name='description_fr',
            field=models.TextField(blank=True, null=True, verbose_name='Description (fr)'),
        ),
        migrations.AlterField(
            model_name='tripsubcategory',
            name='name',
            field=models.CharField(max_length=255, verbose_name='name (en)'),
        ),
        migrations.AlterField(
            model_name='tripsubcategory',
            name='nom',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='name (fr)'),
        ),
    ]
