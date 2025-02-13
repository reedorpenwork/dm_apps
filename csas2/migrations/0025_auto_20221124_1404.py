# Generated by Django 3.2.14 on 2022-11-24 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csas2', '0024_auto_20221118_1137'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='year',
        ),
        migrations.AddField(
            model_name='csasrequestreview',
            name='is_other_mandate',
            field=models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False, verbose_name='does this fall under another scientific mandate?'),
        ),
        migrations.AlterField(
            model_name='csasoffice',
            name='generic_email',
            field=models.EmailField(default='csas@gmail.com', max_length=254, verbose_name='generic email address'),
            preserve_default=False,
        ),
    ]
