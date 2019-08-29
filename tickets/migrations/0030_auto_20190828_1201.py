# Generated by Django 2.2.2 on 2019-08-28 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0029_auto_20190816_0849'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='app',
            field=models.CharField(blank=True, choices=[('general', 'n/a'), ('camp', 'CAMP db'), ('diets', 'Marine diets'), ('esee', 'ESEE (not part of site)'), ('grais', 'grAIS'), ('herring', 'HerMorrhage'), ('ihub', 'iHub'), ('inventory', 'Metadata Inventory'), ('ios2', 'Instruments'), ('masterlist', 'Masterlist'), ('meq', 'Marine environmental quality (MEQ)'), ('oceanography', 'Oceanography'), ('plankton', 'Plankton Net (not part of site)'), ('projects', 'Science project planning'), ('publications', 'Project Publications Inventory'), ('sar_search', 'SAR Search'), ('scifi', 'SciFi'), ('shares', 'Gulf Shares'), ('snowcrab', 'Snowcrab'), ('spot', 'Grants & Contributions (Spot)'), ('staff', 'Staff Planning Tool'), ('tickets', 'Data Management Tickets'), ('trapnet', 'TrapNet'), ('travel', 'Travel Management System'), ('whalesdb', 'Whale Equipment Deployment Inventory')], default='general', max_length=25, null=True, verbose_name='application name'),
        ),
    ]
