# Generated by Django 2.0 on 2022-12-10 18:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0002_auto_20221207_1231'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scorevoting',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scorequestion', to='voting.ScoreQuestion'),
        ),
    ]
