# Generated by Django 2.2.13 on 2020-10-07 11:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('whalesdb', '0010_auto_20201005_1117'),
    ]

    operations = [
        migrations.CreateModel(
            name='EheHydrophoneEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ehe_date', models.DateField(verbose_name='Attachment Date')),
                ('ecp', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='whalesdb.EcpChannelProperty', verbose_name='Channel')),
                ('hyd', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='Hydrophones', to='whalesdb.EqpEquipment', verbose_name='Hydrophone')),
                ('rec', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='Recorders', to='whalesdb.EqpEquipment', verbose_name='Recorder')),
            ],
        ),
        migrations.DeleteModel(
            name='EhaHydrophoneAttachment',
        ),
    ]
