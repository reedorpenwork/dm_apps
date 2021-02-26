# Generated by Django 3.1.2 on 2021-02-26 12:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bio_diversity', '0011_auto_20210225_0831'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='fecundity',
            name='Fecundity_Uniqueness',
        ),
        migrations.RemoveField(
            model_name='fecundity',
            name='evnt_id',
        ),
        migrations.AlterField(
            model_name='envtreatcode',
            name='rec_dose',
            field=models.CharField(blank=True, max_length=400, null=True, verbose_name='Recommended Dosage'),
        ),
        migrations.AlterField(
            model_name='envtreatment',
            name='contx_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='env_treatment', to='bio_diversity.containerxref', verbose_name='Container Cross Reference'),
        ),
        migrations.AlterField(
            model_name='envtreatment',
            name='lot_num',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='Lot Number'),
        ),
        migrations.AddConstraint(
            model_name='fecundity',
            constraint=models.UniqueConstraint(fields=('stok_id', 'coll_id', 'start_date'), name='Fecundity_Uniqueness'),
        ),
    ]
