# Generated by Django 2.2.7 on 2020-03-28 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('headway', '0010_auto_20200327_1406'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
