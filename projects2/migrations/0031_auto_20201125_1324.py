# Generated by Django 3.1.2 on 2020-11-25 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects2', '0030_auto_20201125_1139'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectyear',
            name='allocated_budget',
        ),
        migrations.RemoveField(
            model_name='projectyear',
            name='notification_email_sent',
        ),
        migrations.AddField(
            model_name='review',
            name='total_score',
            field=models.IntegerField(blank=True, editable=False, null=True, verbose_name='total score'),
        ),
    ]
