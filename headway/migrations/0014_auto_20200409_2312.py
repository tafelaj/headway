# Generated by Django 2.2.7 on 2020-04-09 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('headway', '0013_auto_20200409_2310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testgrade',
            name='name',
            field=models.CharField(default='Continuous Assessment', max_length=100),
        ),
    ]
