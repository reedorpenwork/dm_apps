# Generated by Django 3.2.13 on 2022-05-02 15:35

import csas2.models
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shared_models', '0031_subjectmatter_is_csas_request_tag'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(verbose_name='date')),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_lead', models.BooleanField(default=False, verbose_name='lead author?')),
            ],
            options={
                'ordering': ['-is_lead', 'person__first_name', 'person__last_name'],
            },
        ),
        migrations.CreateModel(
            name='CSASAdminUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_national_admin', models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False, verbose_name='national administrator?')),
                ('is_web_pub_user', models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False, verbose_name='NCR web & pub staff?')),
            ],
            options={
                'ordering': ['-is_national_admin', 'user__first_name'],
            },
        ),
        migrations.CreateModel(
            name='CSASOffice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('generic_email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='generic email address')),
                ('disable_request_notifications', models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False, verbose_name='disable notifications of new requests?')),
                ('no_staff_emails', models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False, verbose_name='do not send emails directly to office staff?')),
            ],
            options={
                'ordering': ['region'],
            },
        ),
        migrations.CreateModel(
            name='CSASRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('language', models.IntegerField(choices=[(1, 'English'), (2, 'French')], default=1, verbose_name='language of request')),
                ('title', models.CharField(max_length=1000, verbose_name='title')),
                ('translated_title', models.CharField(blank=True, max_length=1000, null=True, verbose_name='translated title')),
                ('is_multiregional', models.IntegerField(blank=True, choices=[(None, 'Unsure'), (1, 'Yes'), (0, 'No')], default=False, help_text='e.g., frameworks, tools, issues and/or aquatic species widely distributed throughout more than one region', null=True, verbose_name='Could the advice provided potentially be applicable to other regions and/or sectors?')),
                ('multiregional_text', models.TextField(blank=True, null=True, verbose_name='Please list other sectors and/or regions and provide brief rationale')),
                ('issue', models.TextField(blank=True, help_text='Should be phrased as a question to be answered by Science. The text provided here will serve as the objectives for the terms of reference.', null=True, verbose_name='Issue requiring science information and/or advice')),
                ('assistance_text', models.TextField(blank=True, null=True, verbose_name='From whom in Science have you had assistance in developing the question/request (CSAS and/or DFO science staff)')),
                ('rationale', models.TextField(blank=True, help_text='What will the information/advice be used for? Who will be the end user(s)? Will it impact other DFO programs or regions? The text provided here will serve as the context for the terms of reference.', null=True, verbose_name='Rationale or context for the request')),
                ('risk_text', models.TextField(blank=True, null=True, verbose_name='What is the expected consequence if science advice is not provided?')),
                ('advice_needed_by', models.DateTimeField(verbose_name='Latest possible date to receive Science advice')),
                ('rationale_for_timeline', models.TextField(blank=True, help_text='e.g., COSEWIC or consultation meetings, Environmental Assessments, legal or regulatory requirement, Treaty obligation, international commitments, etc). Please elaborate and provide anticipatory dates', null=True, verbose_name='Rationale for deadline?')),
                ('has_funding', models.BooleanField(default=False, help_text='i.e., special analysis, meeting costs, translation)?', verbose_name='Click here if you have funds to cover any extra costs associated with this request?')),
                ('funding_text', models.TextField(blank=True, null=True, verbose_name='Please describe')),
                ('prioritization', models.IntegerField(blank=True, choices=[(1, 'High'), (2, 'Medium'), (3, 'Low')], null=True, verbose_name='How would you classify the prioritization of this request?')),
                ('prioritization_text', models.TextField(blank=True, null=True, verbose_name='What is the rationale behind the prioritization?')),
                ('status', models.IntegerField(choices=[(1, 'Draft'), (2, 'Submitted'), (3, 'Ready for review'), (4, 'Under review'), (5, 'Fulfilled'), (6, 'Withdrawn'), (11, 'Reviewed'), (12, 'Flagged'), (13, 'Re-scoping')], default=1, editable=False, verbose_name='status')),
                ('submission_date', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='submission date')),
                ('old_id', models.IntegerField(blank=True, editable=False, null=True)),
                ('uuid', models.UUIDField(blank=True, default=uuid.uuid4, editable=False, null=True, unique=True, verbose_name='unique identifier')),
                ('ref_number', models.CharField(blank=True, editable=False, max_length=255, null=True, verbose_name='reference number')),
            ],
            options={
                'verbose_name': 'CSAS Request',
                'verbose_name_plural': 'CSAS Requests',
                'ordering': ('fiscal_year', 'title'),
            },
        ),
        migrations.CreateModel(
            name='CSASRequestFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('caption', models.CharField(max_length=255, verbose_name='caption')),
                ('date_created', models.DateTimeField(auto_now=True)),
                ('is_approval', models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False, verbose_name='is this file an approval for this request?')),
                ('file', models.FileField(upload_to=csas2.models.request_directory_path)),
            ],
            options={
                'ordering': ['-date_created'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CSASRequestNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('type', models.IntegerField(choices=[(1, 'General comment'), (2, 'To Do')], verbose_name='type')),
                ('note', models.TextField(verbose_name='note')),
                ('is_complete', models.BooleanField(default=False, verbose_name='complete?')),
            ],
            options={
                'ordering': ['is_complete', '-updated_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CSASRequestReview',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('ref_number', models.CharField(blank=True, max_length=50, null=True, verbose_name='reference number (optional)')),
                ('is_valid', models.IntegerField(blank=True, choices=[(1, 'Yes'), (0, 'No')], null=True, verbose_name='Is this within the scope of CSAS?')),
                ('is_feasible', models.IntegerField(blank=True, choices=[(1, 'Yes'), (0, 'No'), (9, 'Unsure')], null=True, verbose_name='is this feasible from a Science perspective')),
                ('decision', models.IntegerField(blank=True, choices=[(1, 'Screen-in'), (2, 'Return to client'), (3, 'Re-scope')], null=True, verbose_name='recommendation')),
                ('decision_text', models.TextField(blank=True, null=True, verbose_name='recommendation explanation')),
                ('decision_date', models.DateTimeField(blank=True, null=True, verbose_name='recommendation date')),
                ('advice_date', models.DateTimeField(blank=True, null=True, verbose_name='advice required by (final)')),
                ('deferred_text', models.TextField(blank=True, null=True, verbose_name='rationale for alternate scheduling')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='administrative notes')),
                ('email_notification_date', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='email notification date')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title_en', models.CharField(blank=True, max_length=255, null=True, verbose_name='title (English)')),
                ('title_fr', models.CharField(blank=True, max_length=255, null=True, verbose_name='title (French)')),
                ('title_in', models.CharField(blank=True, max_length=255, null=True, verbose_name='title (Inuktitut)')),
                ('year', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(9999)], verbose_name='Publication Year')),
                ('pages', models.IntegerField(blank=True, null=True, verbose_name='pages')),
                ('file_en', models.FileField(blank=True, null=True, upload_to=csas2.models.doc_directory_path, verbose_name='file attachment (en)')),
                ('file_fr', models.FileField(blank=True, null=True, upload_to=csas2.models.doc_directory_path, verbose_name='file attachment (fr)')),
                ('url_en', models.URLField(blank=True, max_length=2000, null=True, verbose_name='document url (en)')),
                ('url_fr', models.URLField(blank=True, max_length=2000, null=True, verbose_name='document url (fr)')),
                ('dev_link_en', models.URLField(blank=True, max_length=2000, null=True, verbose_name='dev link (en)')),
                ('dev_link_fr', models.URLField(blank=True, max_length=2000, null=True, verbose_name='dev link (fr)')),
                ('ekme_gcdocs_en', models.CharField(blank=True, max_length=255, null=True, verbose_name='EKME# / GCDocs (en)')),
                ('ekme_gcdocs_fr', models.CharField(blank=True, max_length=255, null=True, verbose_name='EKME# / GCDocs (fr)')),
                ('lib_cat_en', models.CharField(blank=True, max_length=255, null=True, verbose_name='library catalogue # (en)')),
                ('lib_cat_fr', models.CharField(blank=True, max_length=255, null=True, verbose_name='library catalogue # (fr)')),
                ('due_date', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='document due date')),
                ('pub_number_request_date', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='date of publication number request')),
                ('pub_number', models.CharField(blank=True, editable=False, max_length=25, null=True, unique=True, verbose_name='publication number')),
                ('status', models.IntegerField(choices=[(0, 'OK'), (1, 'Tracking initiated'), (2, 'Submitted by author'), (3, 'Under review by chair'), (4, 'Approved by chair'), (5, 'Under review by CSAS coordinator'), (6, 'Approved by CSAS coordinator'), (13, 'Under review by section head'), (14, 'Approved by section head'), (15, 'Under review by division manager'), (16, 'Approved by division manager'), (7, 'Under review by director'), (8, 'Approved by director'), (9, 'Submitted to CSAS office'), (10, 'Proof sent to author'), (11, 'Proof approved by author'), (12, 'Posted'), (17, 'Posted (updated)')], default=1, editable=False, verbose_name='status')),
                ('translation_status', models.IntegerField(choices=[(0, '----'), (1, 'In progress'), (2, 'Translated, unreviewed'), (3, 'Translated, reviewed')], default=0, editable=False, verbose_name='translation status')),
                ('old_id', models.IntegerField(blank=True, editable=False, null=True)),
            ],
            options={
                'ordering': ['process', 'title_en'],
            },
        ),
        migrations.CreateModel(
            name='DocumentNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('type', models.IntegerField(choices=[(1, 'General comment'), (2, 'To Do')], verbose_name='type')),
                ('note', models.TextField(verbose_name='note')),
                ('is_complete', models.BooleanField(default=False, verbose_name='complete?')),
            ],
            options={
                'ordering': ['is_complete', '-updated_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DocumentTracking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('due_date', models.DateTimeField(blank=True, null=True, verbose_name='product due date')),
                ('submission_date', models.DateTimeField(blank=True, null=True, verbose_name='date submitted by author')),
                ('date_chair_sent', models.DateTimeField(blank=True, null=True, verbose_name='date sent to chair')),
                ('date_chair_appr', models.DateTimeField(blank=True, null=True, verbose_name='date approved by chair')),
                ('chair_comments', models.TextField(blank=True, null=True, verbose_name='comment')),
                ('date_coordinator_sent', models.DateTimeField(blank=True, null=True, verbose_name='date sent to CSAS coordinator')),
                ('date_coordinator_appr', models.DateTimeField(blank=True, null=True, verbose_name='date approved by CSAS coordinator')),
                ('coordinator_comments', models.TextField(blank=True, null=True, verbose_name='comment')),
                ('date_section_head_sent', models.DateTimeField(blank=True, null=True, verbose_name='date sent to section head')),
                ('date_section_head_appr', models.DateTimeField(blank=True, null=True, verbose_name='date approved by section head')),
                ('section_head_comments', models.TextField(blank=True, null=True, verbose_name='comment')),
                ('date_division_manager_sent', models.DateTimeField(blank=True, null=True, verbose_name='date sent to division manager')),
                ('date_division_manager_appr', models.DateTimeField(blank=True, null=True, verbose_name='date approved by division manager')),
                ('division_manager_comments', models.TextField(blank=True, null=True, verbose_name='comment')),
                ('date_director_sent', models.DateTimeField(blank=True, null=True, verbose_name='date sent to director')),
                ('date_director_appr', models.DateTimeField(blank=True, null=True, verbose_name='date approved by director')),
                ('director_comments', models.TextField(blank=True, null=True, verbose_name='comment')),
                ('pub_number', models.CharField(blank=True, max_length=25, null=True, verbose_name='publication number')),
                ('date_doc_submitted', models.DateTimeField(blank=True, null=True, verbose_name='date document submitted to CSAS office')),
                ('date_proof_author_sent', models.DateTimeField(blank=True, null=True, verbose_name='date PDF proof sent to author')),
                ('date_proof_author_approved', models.DateTimeField(blank=True, null=True, verbose_name='date PDF proof approved by author')),
                ('anticipated_posting_date', models.DateTimeField(blank=True, null=True, verbose_name='anticipated posting date')),
                ('actual_posting_date', models.DateTimeField(blank=True, null=True, verbose_name='actual posting date')),
                ('updated_posting_date', models.DateTimeField(blank=True, null=True, verbose_name='updated posting date')),
                ('is_in_house', models.BooleanField(default=False, verbose_name='Will translation be tackled in-house?')),
                ('target_lang', models.IntegerField(blank=True, choices=[(1, 'English'), (2, 'French')], null=True, verbose_name='target language')),
                ('date_translation_sent', models.DateTimeField(blank=True, null=True, verbose_name='date sent to translation')),
                ('anticipated_return_date', models.DateTimeField(blank=True, null=True, verbose_name='forecasted return date')),
                ('client_ref_number', models.CharField(blank=True, max_length=255, null=True, verbose_name='client reference number')),
                ('translation_ref_number', models.CharField(blank=True, max_length=255, null=True, verbose_name='translation reference number')),
                ('is_urgent', models.BooleanField(default=False, verbose_name='was submitted as an urgent request?')),
                ('date_returned', models.DateTimeField(blank=True, null=True, verbose_name='date received from translation')),
                ('invoice_number', models.CharField(blank=True, max_length=255, null=True, verbose_name='invoice number')),
                ('translation_review_date', models.DateTimeField(blank=True, null=True, verbose_name='translation review completion date')),
                ('translation_notes', models.TextField(blank=True, null=True, verbose_name='translation notes')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DocumentType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='name (en)')),
                ('nom', models.CharField(blank=True, max_length=255, null=True, verbose_name='name (fr)')),
                ('days_due', models.IntegerField(blank=True, null=True, verbose_name='days due following meeting')),
                ('hide_from_list', models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False, verbose_name='hide from main search?')),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Invitee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(0, 'Invited'), (1, 'Accepted'), (2, 'Declined'), (3, 'Tentative'), (4, 'Proposed')], default=9, verbose_name='status')),
                ('invitation_sent_date', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='date invitation was sent')),
                ('comments', models.TextField(blank=True, null=True, verbose_name='comments')),
            ],
            options={
                'ordering': ['person__first_name', 'person__last_name'],
            },
        ),
        migrations.CreateModel(
            name='InviteeRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='name (en)')),
                ('nom', models.CharField(blank=True, max_length=255, null=True, verbose_name='name (fr)')),
                ('category', models.IntegerField(blank=True, choices=[(1, 'chair'), (2, 'client lead'), (3, 'steering committee member'), (4, 'science lead'), (5, 'csas coordinator'), (6, 'science advisor'), (7, 'CSAS office contact')], null=True, verbose_name='special category')),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(blank=True, max_length=1000, null=True, verbose_name='title (en)')),
                ('nom', models.CharField(blank=True, max_length=1000, null=True, verbose_name='title (fr)')),
                ('is_planning', models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False, verbose_name='Is this a planning meeting?')),
                ('is_virtual', models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False, verbose_name='Is this a virtual meeting?')),
                ('location', models.CharField(blank=True, help_text='City, State/Province, Country or Virtual', max_length=1000, null=True, verbose_name='location')),
                ('start_date', models.DateTimeField(null=True, verbose_name='initial activity date')),
                ('end_date', models.DateTimeField(null=True, verbose_name='anticipated end date')),
                ('is_estimate', models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False, help_text="By selecting yes, the meeting date will be displayed in the 'quarter/year' format, e.g.: Summer 2024", verbose_name='The dates provided above are approximations')),
                ('time_description_en', models.CharField(blank=True, help_text='e.g.: 9am to 4pm (Atlantic)', max_length=1000, null=True, verbose_name='description of meeting times (en)')),
                ('time_description_fr', models.CharField(blank=True, help_text='e.g.: 9h à 16h (Atlantique)', max_length=1000, null=True, verbose_name='description of meeting times (fr)')),
                ('somp_notification_date', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='CSAS office notified about SoMP')),
            ],
            options={
                'ordering': ['-is_planning', 'start_date'],
            },
        ),
        migrations.CreateModel(
            name='MeetingFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('caption', models.CharField(max_length=255, verbose_name='caption')),
                ('date_created', models.DateTimeField(auto_now=True)),
                ('file', models.FileField(upload_to=csas2.models.meeting_directory_path)),
                ('is_somp', models.BooleanField(default=False, verbose_name='is this the SoMP?')),
            ],
            options={
                'ordering': ['-date_created'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MeetingNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('type', models.IntegerField(choices=[(1, 'General comment'), (2, 'To Do')], verbose_name='type')),
                ('note', models.TextField(verbose_name='note')),
                ('is_complete', models.BooleanField(default=False, verbose_name='complete?')),
            ],
            options={
                'ordering': ['is_complete', '-updated_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MeetingResource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(blank=True, max_length=255, null=True, verbose_name='name (fr)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, verbose_name='name (en)')),
                ('url_en', models.URLField(blank=True, max_length=2000, null=True, verbose_name='url (English)')),
                ('url_fr', models.URLField(blank=True, max_length=2000, null=True, verbose_name='url (French)')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Process',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(blank=True, default=uuid.uuid4, editable=False, null=True, unique=True, verbose_name='unique identifier')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(blank=True, max_length=1000, null=True, verbose_name='title (en)')),
                ('nom', models.CharField(blank=True, max_length=1000, null=True, verbose_name='title (fr)')),
                ('status', models.IntegerField(choices=[(1, 'Initiated'), (10, 'Tentative'), (20, 'On'), (22, 'ToR Complete'), (25, 'Meeting Complete'), (30, 'Deferred'), (100, 'Complete'), (90, 'Withdrawn')], default=1, verbose_name='status')),
                ('scope', models.IntegerField(choices=[(1, 'Regional'), (2, 'Zonal'), (3, 'National')], verbose_name='scope')),
                ('type', models.IntegerField(choices=[(1, 'Advisory Meeting'), (2, 'Science Response Process')], verbose_name='type')),
                ('advice_date', models.DateTimeField(blank=True, null=True, verbose_name='Target date for to provide Science advice')),
                ('is_posted', models.BooleanField(default=False, verbose_name='is meeting posted on CSAS website?')),
                ('has_peer_review_meeting', models.BooleanField(default=False, verbose_name='has peer review meeting?')),
                ('has_planning_meeting', models.BooleanField(default=False, verbose_name='has planning meeting?')),
                ('posting_request_date', models.DateTimeField(blank=True, null=True, verbose_name='Date of posting request')),
                ('posting_notification_date', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='Posting notification date')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='process_created_by', to=settings.AUTH_USER_MODEL)),
                ('csas_requests', models.ManyToManyField(blank=True, related_name='processes', to='csas2.CSASRequest', verbose_name='Connected CSAS requests')),
                ('editors', models.ManyToManyField(blank=True, help_text='A list of non-CSAS staff with permissions to edit the process, meetings and documents', related_name='process_editors', to=settings.AUTH_USER_MODEL, verbose_name='process editors')),
                ('fiscal_year', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.DO_NOTHING, related_name='processes', to='shared_models.fiscalyear', verbose_name='fiscal year')),
                ('lead_office', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='csas_lead_offices', to='csas2.csasoffice', verbose_name='lead CSAS office')),
                ('other_offices', models.ManyToManyField(blank=True, to='csas2.CSASOffice', verbose_name='other CSAS offices')),
            ],
            options={
                'ordering': ['fiscal_year', 'name'],
            },
        ),
        migrations.CreateModel(
            name='TermsOfReference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('context_en', models.TextField(blank=True, help_text='English', null=True, verbose_name='context (en)')),
                ('context_fr', models.TextField(blank=True, help_text='French', null=True, verbose_name='context (fr)')),
                ('objectives_en', models.TextField(blank=True, help_text='English', null=True, verbose_name='objectives (en)')),
                ('objectives_fr', models.TextField(blank=True, help_text='French', null=True, verbose_name='objectives (fr)')),
                ('participation_en', models.TextField(blank=True, help_text='English', null=True, verbose_name='participation (en)')),
                ('participation_fr', models.TextField(blank=True, help_text='French', null=True, verbose_name='participation (fr)')),
                ('references_en', models.TextField(blank=True, help_text='English', null=True, verbose_name='references (en)')),
                ('references_fr', models.TextField(blank=True, help_text='French', null=True, verbose_name='references (fr)')),
                ('status', models.IntegerField(choices=[(10, 'Draft'), (20, 'Under review'), (30, 'Awaiting changes'), (35, 'Reviewed'), (40, 'Awaiting posting'), (50, 'Posted')], default=10, editable=False, verbose_name='status')),
                ('submission_date', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='submission date')),
                ('posting_request_date', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='Date of posting request')),
                ('posting_notification_date', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='Posting notification date')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='termsofreference_created_by', to=settings.AUTH_USER_MODEL)),
                ('expected_document_types', models.ManyToManyField(blank=True, to='csas2.DocumentType', verbose_name='expected publications')),
                ('meeting', models.OneToOneField(blank=True, help_text='The ToR will pull several fields from the linked meeting (e.g., dates, chair, location, ...)', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='tor', to='csas2.meeting', verbose_name='Linked to which meeting?')),
                ('process', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='tor', to='csas2.process')),
                ('updated_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='termsofreference_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ToRReviewer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order', models.IntegerField(null=True, verbose_name='process order')),
                ('decision', models.IntegerField(blank=True, choices=[(1, 'Accept'), (2, 'Request changes')], null=True, verbose_name='decision')),
                ('decision_date', models.DateTimeField(blank=True, null=True, verbose_name='date')),
                ('comments', models.TextField(blank=True, null=True, verbose_name='comments')),
                ('status', models.IntegerField(choices=[(10, 'Draft'), (20, 'Queued'), (30, 'Pending'), (40, 'Complete')], default=10, verbose_name='status')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='torreviewer_created_by', to=settings.AUTH_USER_MODEL)),
                ('tor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviewers', to='csas2.termsofreference')),
                ('updated_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='torreviewer_updated_by', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='tor_reviews', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'ToR reviewer',
                'ordering': ['tor', 'order'],
            },
        ),
        migrations.CreateModel(
            name='ProcessNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('type', models.IntegerField(choices=[(1, 'General comment'), (2, 'To Do')], verbose_name='type')),
                ('note', models.TextField(verbose_name='note')),
                ('is_complete', models.BooleanField(default=False, verbose_name='complete?')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='processnote_created_by', to=settings.AUTH_USER_MODEL)),
                ('process', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='csas2.process')),
                ('updated_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='processnote_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['is_complete', '-updated_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProcessCost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cost_category', models.IntegerField(choices=[(1, 'Translation'), (2, 'Travel'), (3, 'Hospitality'), (4, 'Space rental'), (5, 'Simultaneous translation'), (9, 'Other')], verbose_name='cost category')),
                ('description', models.CharField(blank=True, max_length=1000, null=True, verbose_name='description')),
                ('funding_source', models.CharField(blank=True, max_length=255, null=True, verbose_name='funding source')),
                ('amount', models.FloatField(default=0, verbose_name='amount (CAD)')),
                ('process', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='costs', to='csas2.process', verbose_name='process')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
