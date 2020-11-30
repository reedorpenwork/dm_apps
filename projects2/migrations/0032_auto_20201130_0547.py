# Generated by Django 3.1.2 on 2020-11-30 09:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects2', '0031_auto_20201125_1324'),
    ]

    operations = [
        migrations.AlterField(
            model_name='milestoneupdate',
            name='status',
            field=models.IntegerField(choices=[(7, 'In progress'), (8, 'Completed'), (9, 'Aborted / cancelled')], default=7, editable=False),
        ),
        migrations.AlterField(
            model_name='review',
            name='collaboration_comment',
            field=models.TextField(blank=True, null=True, verbose_name='External Pressures comments'),
        ),
        migrations.AlterField(
            model_name='review',
            name='collaboration_score',
            field=models.IntegerField(blank=True, choices=[(3, 'high'), (2, 'medium'), (1, 'low')], null=True, verbose_name='External Pressures'),
        ),
        migrations.AlterField(
            model_name='review',
            name='ecological_comment',
            field=models.TextField(blank=True, null=True, verbose_name='Ecological Impact comments'),
        ),
        migrations.AlterField(
            model_name='review',
            name='ecological_score',
            field=models.IntegerField(blank=True, choices=[(3, 'high'), (2, 'medium'), (1, 'low')], null=True, verbose_name='Ecological Impact'),
        ),
        migrations.AlterField(
            model_name='review',
            name='operational_comment',
            field=models.TextField(blank=True, null=True, verbose_name='Operational Considerations comments'),
        ),
        migrations.AlterField(
            model_name='review',
            name='operational_score',
            field=models.IntegerField(blank=True, choices=[(3, 'high'), (2, 'medium'), (1, 'low')], null=True, verbose_name='Operational Considerations'),
        ),
        migrations.AlterField(
            model_name='review',
            name='strategic_comment',
            field=models.TextField(blank=True, null=True, verbose_name='Strategic Direction comments'),
        ),
        migrations.AlterField(
            model_name='review',
            name='strategic_score',
            field=models.IntegerField(blank=True, choices=[(3, 'high'), (2, 'medium'), (1, 'low')], null=True, verbose_name='Strategic Direction'),
        ),
        migrations.AlterField(
            model_name='statusreport',
            name='major_accomplishments',
            field=models.TextField(blank=True, null=True, verbose_name='major accomplishments'),
        ),
        migrations.AlterField(
            model_name='statusreport',
            name='modified_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='last_mod_by_projects_status_report', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='statusreport',
            name='section_head_reviewed',
            field=models.BooleanField(default=False, editable=False, verbose_name='reviewed by section head'),
        ),
        migrations.AlterField(
            model_name='statusreport',
            name='status',
            field=models.IntegerField(choices=[(3, 'On-track'), (4, 'Complete'), (5, 'Encountering issues'), (6, 'Aborted / cancelled')], default=1),
        ),
    ]
