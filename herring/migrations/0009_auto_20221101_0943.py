# Generated by Django 3.2.14 on 2022-11-01 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herring', '0008_auto_20221101_0843'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='species',
            name='a_coef',
        ),
        migrations.RemoveField(
            model_name='species',
            name='b_coef',
        ),
        migrations.AddField(
            model_name='species',
            name='a_female',
            field=models.FloatField(blank=True, help_text='The A regression coefficient in the relationship between female length and weight.', null=True, verbose_name='length weight A (female)'),
        ),
        migrations.AddField(
            model_name='species',
            name='a_male',
            field=models.FloatField(blank=True, help_text='The A regression coefficient in the relationship between male length and weight.', null=True, verbose_name='length weight A (male)'),
        ),
        migrations.AddField(
            model_name='species',
            name='a_unk',
            field=models.FloatField(blank=True, help_text='The A regression coefficient in the relationship between length and weight for unspecified sex.', null=True, verbose_name='length weight A (unspecified)'),
        ),
        migrations.AddField(
            model_name='species',
            name='b_female',
            field=models.FloatField(blank=True, help_text='The B regression coefficient in the relationship between female length and weight.', null=True, verbose_name='length weight B (female)'),
        ),
        migrations.AddField(
            model_name='species',
            name='b_male',
            field=models.FloatField(blank=True, help_text='The B regression coefficient in the relationship between male length and weight.', null=True, verbose_name='length weight B (male)'),
        ),
        migrations.AddField(
            model_name='species',
            name='b_unk',
            field=models.FloatField(blank=True, help_text='The A regression coefficient in the relationship between length and weight for unspecified sex.', null=True, verbose_name='length weight B (unspecified)'),
        ),
        migrations.AddField(
            model_name='species',
            name='min_length',
            field=models.IntegerField(blank=True, help_text='What is the minimum length of this species before which a user should receive a warning?', null=True, verbose_name='minimum length'),
        ),
        migrations.AddField(
            model_name='species',
            name='min_weight',
            field=models.IntegerField(blank=True, help_text='What is the minimum length of this species before which a user should receive a warning?', null=True, verbose_name='minimum length'),
        ),
        migrations.AlterField(
            model_name='species',
            name='max_annulus_count',
            field=models.IntegerField(blank=True, help_text='Any observations beyond this mark will prompt a warning', null=True, verbose_name='maximum annulus count'),
        ),
        migrations.AlterField(
            model_name='species',
            name='max_gonad_weight',
            field=models.IntegerField(blank=True, help_text='Any observations beyond this mark will prompt a warning', null=True, verbose_name='maximum gonad weight'),
        ),
        migrations.AlterField(
            model_name='species',
            name='max_length',
            field=models.IntegerField(blank=True, help_text='Any observations beyond this mark will prompt a warning', null=True, verbose_name='maximum length'),
        ),
        migrations.AlterField(
            model_name='species',
            name='max_weight',
            field=models.IntegerField(blank=True, help_text='Any observations beyond this mark will prompt a warning', null=True, verbose_name='maximum fish weight'),
        ),
    ]
