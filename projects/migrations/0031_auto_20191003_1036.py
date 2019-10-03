# Generated by Django 2.2.2 on 2019-10-03 13:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0030_remove_file_caption'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='milestone',
            options={'ordering': ['project', 'name']},
        ),
        migrations.RemoveField(
            model_name='milestone',
            name='notes',
        ),
        migrations.AddField(
            model_name='milestone',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='description'),
        ),
        migrations.CreateModel(
            name='MilestoneProgressUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('milestone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='updates', to='projects.Milestone')),
                ('status', models.ForeignKey(default=9, limit_choices_to={'used_for': 3}, on_delete=django.db.models.deletion.DO_NOTHING, related_name='updates', to='projects.Status')),
                ('status_report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='updates', to='projects.StatusReport')),
            ],
            options={
                'ordering': ['status_report', 'status'],
            },
        ),
    ]
