# Generated by Django 2.0.7 on 2018-09-08 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profiledata',
            name='favourite_problem_type',
            field=models.TextField(blank=True, default='{}'),
        ),
    ]
