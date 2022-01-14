# Generated by Django 3.2.10 on 2022-01-07 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ppt', '0019_activity_parent'),
        ('csas2', '0011_alter_process_projects'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='termsofreference',
            name='is_complete',
        ),
        migrations.AddField(
            model_name='invitee',
            name='comments',
            field=models.TextField(blank=True, null=True, verbose_name='comments'),
        ),
        migrations.AlterField(
            model_name='process',
            name='projects',
            field=models.ManyToManyField(blank=True, related_name='csas_processes', to='ppt.Project', verbose_name='Links to PPT Projects'),
        ),
        migrations.AlterField(
            model_name='torreviewer',
            name='comments',
            field=models.TextField(blank=True, null=True, verbose_name='comments'),
        ),
    ]
