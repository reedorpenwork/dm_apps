# Generated by Django 3.2.4 on 2021-11-02 10:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('masterlist', '0011_alter_sector_unique_together'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('maret', '0005_auto_20211029_0802'),
    ]

    operations = [
        migrations.CreateModel(
            name='HelpText',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model', models.CharField(blank=True, max_length=255, null=True)),
                ('field_name', models.CharField(max_length=255)),
                ('eng_text', models.TextField(verbose_name='English text')),
                ('fra_text', models.TextField(blank=True, null=True, verbose_name='French text')),
            ],
            options={
                'ordering': ['field_name'],
            },
        ),
        migrations.AlterField(
            model_name='interaction',
            name='dfo_liaison',
            field=models.ManyToManyField(blank=True, related_name='interaction_dfo_liaison', to=settings.AUTH_USER_MODEL, verbose_name='DFO liaison/secretariat'),
        ),
        migrations.AlterField(
            model_name='interaction',
            name='main_topic',
            field=models.ManyToManyField(blank=True, related_name='main_topics', to='maret.DiscussionTopic', verbose_name='Main Topic(s) of discussion'),
        ),
        migrations.AlterField(
            model_name='interaction',
            name='other_dfo_participants',
            field=models.ManyToManyField(blank=True, related_name='interaction_dfo_participants', to=settings.AUTH_USER_MODEL, verbose_name='Other DFO participants/contributors'),
        ),
        migrations.AlterField(
            model_name='interaction',
            name='species',
            field=models.ManyToManyField(blank=True, related_name='species', to='maret.Species', verbose_name='Main species of discussion'),
        ),
        migrations.CreateModel(
            name='ContactExtension',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(default='N/A', max_length=255, verbose_name='Role')),
                ('contact', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='ext_con', to='masterlist.person', verbose_name='Contact')),
            ],
        ),
    ]
