# Generated by Django 2.2.2 on 2020-05-14 00:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0012_auto_20200513_2131'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='purpose',
            options={},
        ),
        migrations.AlterModelOptions(
            name='trippurpose',
            options={},
        ),
        migrations.AddField(
            model_name='njcrates',
            name='nom',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='njcrates',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
