# Generated by Django 3.2.5 on 2021-12-08 11:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shared_models', '0030_remove_river_fishing_area_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='AchievementCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='name (en)')),
                ('nom', models.CharField(blank=True, max_length=255, null=True, verbose_name='name (fr)')),
                ('code', models.CharField(max_length=5, unique=True, verbose_name='category code')),
                ('is_publication', models.BooleanField(default=False, verbose_name='Is this a category for publications?')),
            ],
            options={
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('application_start_date', models.DateTimeField(verbose_name='period covered by this application (start) ')),
                ('application_end_date', models.DateTimeField(verbose_name='period covered by this application (end) ')),
                ('current_position_title', models.CharField(blank=True, max_length=255, null=True, verbose_name='position title')),
                ('work_location', models.CharField(blank=True, max_length=1000, null=True, verbose_name='work location')),
                ('last_application', models.DateTimeField(blank=True, null=True, verbose_name='last application for advancement')),
                ('last_promotion', models.DateTimeField(blank=True, null=True, verbose_name='last promotion')),
                ('academic_background', models.TextField(blank=True, null=True, verbose_name='academic background')),
                ('employment_history', models.TextField(blank=True, null=True, verbose_name='employment history')),
                ('objectives', models.TextField(blank=True, help_text='no more than 200 words', null=True, verbose_name='department / sectoral objectives')),
                ('relevant_factors', models.TextField(blank=True, help_text='no more than 400 words', null=True, verbose_name='relevant factors')),
                ('submission_date', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='submission date')),
                ('status', models.IntegerField(choices=[(10, 'Draft'), (20, 'Submitted'), (30, 'Awaiting manager decision'), (40, 'Awaiting applicant signature'), (50, 'Under further review'), (90, 'Not approved'), (100, 'Approved')], default=10, editable=False, verbose_name='status')),
                ('applicant', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='res_applications', to=settings.AUTH_USER_MODEL, verbose_name='researcher')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='application_created_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Context',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='name (en)')),
                ('nom', models.CharField(blank=True, max_length=255, null=True, verbose_name='name (fr)')),
                ('description_en', models.TextField(blank=True, null=True, verbose_name='Description (en)')),
                ('description_fr', models.TextField(blank=True, null=True, verbose_name='Description (fr)')),
                ('word_limit', models.IntegerField(default=500, verbose_name='word limit')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GroupLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='name')),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PublicationType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='name (en)')),
                ('nom', models.CharField(blank=True, max_length=255, null=True, verbose_name='name (fr)')),
                ('code', models.CharField(max_length=5, verbose_name='display code')),
            ],
            options={
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='ReviewType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='name (en)')),
                ('nom', models.CharField(blank=True, max_length=255, null=True, verbose_name='name (fr)')),
                ('code', models.CharField(blank=True, max_length=5, null=True, verbose_name='display code')),
            ],
            options={
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='SiteSection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section', models.IntegerField(choices=[(1, 'ANNEX A'), (2, 'ANNEX B'), (3, 'For new applications')], unique=True, verbose_name='section')),
                ('description_en', models.TextField(blank=True, null=True, verbose_name='Description (en)')),
                ('description_fr', models.TextField(blank=True, null=True, verbose_name='Description (fr)')),
            ],
            options={
                'ordering': ['section'],
            },
        ),
        migrations.CreateModel(
            name='ResSubUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_admin', models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False, verbose_name='app administrator?')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='res_sub_user', to=settings.AUTH_USER_MODEL, verbose_name='DM Apps user')),
            ],
            options={
                'ordering': ['-is_admin', 'user__first_name'],
            },
        ),
        migrations.CreateModel(
            name='Recommendation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('recommendation_text', models.TextField(blank=True, help_text='no more than 250 words', null=True, verbose_name="accountable manager's assessment")),
                ('decision', models.IntegerField(blank=True, choices=[(1, 'In my opinion, the dossier contains sufficient evidence to warrant consideration of the application by the appropriate committee.'), (2, 'In my opinion, the dossier does not contain sufficient evidence to warrant consideration of the application by the appropriate committee.')], null=True, verbose_name='decision')),
                ('applicant_comment', models.TextField(blank=True, help_text='no more than 250 words', null=True, verbose_name="researcher's comment")),
                ('manager_signed', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='manager signature')),
                ('applicant_signed', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='researcher signature')),
                ('applicant_signed_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='res_applicant_signed_by_recommendations', to=settings.AUTH_USER_MODEL, verbose_name='applicant signed by')),
                ('application', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='recommendation', to='res.application')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='recommendation_created_by', to=settings.AUTH_USER_MODEL)),
                ('manager_signed_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='res_manager_signed_by_recommendations', to=settings.AUTH_USER_MODEL, verbose_name='manager signed by')),
                ('updated_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='recommendation_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Outcome',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='name (en)')),
                ('description_en', models.TextField(blank=True, null=True, verbose_name='Description (en)')),
                ('nom', models.CharField(blank=True, max_length=255, null=True, verbose_name='name (fr)')),
                ('description_fr', models.TextField(blank=True, null=True, verbose_name='Description (fr)')),
                ('order', models.IntegerField(blank=True, null=True, verbose_name='order')),
                ('context', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='outcomes', to='res.context', verbose_name='context')),
            ],
            options={
                'ordering': ['context', 'order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='ApplicationOutcome',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('text', models.TextField(blank=True, null=True, verbose_name='text')),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outcomes', to='res.application')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='applicationoutcome_created_by', to=settings.AUTH_USER_MODEL)),
                ('outcome', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outcomes', to='res.outcome')),
                ('updated_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='applicationoutcome_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='application',
            name='current_group_level',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='applications_current', to='res.grouplevel', verbose_name='Current group / level'),
        ),
        migrations.AddField(
            model_name='application',
            name='fiscal_year',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='res_applications', to='shared_models.fiscalyear', verbose_name='fiscal year'),
        ),
        migrations.AddField(
            model_name='application',
            name='manager',
            field=models.ForeignKey(help_text='This is the person who will provide a recommendation on this application', on_delete=django.db.models.deletion.DO_NOTHING, related_name='manager_res_applications', to=settings.AUTH_USER_MODEL, verbose_name='accountable manager'),
        ),
        migrations.AddField(
            model_name='application',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='res_applications', to='shared_models.section', verbose_name='DFO section'),
        ),
        migrations.AddField(
            model_name='application',
            name='target_group_level',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='applications_target', to='res.grouplevel', verbose_name='Group / level being sought'),
        ),
        migrations.AddField(
            model_name='application',
            name='updated_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='application_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('date', models.DateTimeField(blank=True, null=True, verbose_name='date of publication / achievement')),
                ('detail', models.TextField(verbose_name='detail')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='achievements', to='res.achievementcategory', verbose_name='achievement category')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='achievement_created_by', to=settings.AUTH_USER_MODEL)),
                ('publication_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='achievements', to='res.publicationtype', verbose_name='publication type')),
                ('review_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='achievements', to='res.reviewtype', verbose_name='peer review type')),
                ('updated_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='achievement_updated_by', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='achievements', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['category', 'publication_type', '-date', 'id'],
            },
        ),
    ]
