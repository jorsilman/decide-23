# Generated by Django 2.0 on 2022-12-14 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_auto_20221212_1651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='type',
            field=models.CharField(choices=[('V', 'Voting'), ('BV', 'BinaryVoting'), ('SV', 'ScoreVoting')], default='V', max_length=2),
        ),
    ]
