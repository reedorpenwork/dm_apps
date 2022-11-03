# Generated by Django 3.2.14 on 2022-11-02 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herring', '0014_auto_20221101_1138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fishdetailflag',
            name='flag_definition',
            field=models.IntegerField(choices=[(1, 'The fish length is outside of the probable range.'), (2, 'The fish weight is outside of the probable range.'), (3, 'The gonad weight is outside of the probable range.'), (4, 'The annulus count is outside of the probable range.'), (10, 'Unexpected fish length to weight ratio.'), (11, 'Unexpected gonad weight to somatic weight to maturity level combination.'), (12, 'Unexpected fish length to number of annuli ratio.')]),
        ),
    ]
