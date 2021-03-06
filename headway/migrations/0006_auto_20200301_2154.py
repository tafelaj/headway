# Generated by Django 2.2.7 on 2020-03-01 19:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('headway', '0005_auto_20200228_0104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='institution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='headway.Institution'),
        ),
        migrations.AlterField(
            model_name='program',
            name='institution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='headway.Institution'),
        ),
        migrations.AlterField(
            model_name='program',
            name='level',
            field=models.CharField(choices=[('Certificate', 'Certificate'), ('Diploma', 'Diploma'), ('Bachelor', 'Bachelor'), ('Masters', 'Masters')], help_text='Qualification Level For The Program.', max_length=11),
        ),
        migrations.AlterField(
            model_name='student',
            name='level',
            field=models.CharField(choices=[('Certificate', 'Certificate'), ('Diploma', 'Diploma'), ('Bachelor', 'Bachelor'), ('Masters', 'Masters')], default=1, max_length=100),
        ),
    ]
