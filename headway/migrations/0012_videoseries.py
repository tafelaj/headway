# Generated by Django 2.2.7 on 2020-04-07 11:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('headway', '0011_student_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoSeries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_created=True, auto_now_add=True)),
                ('name', models.CharField(max_length=50)),
                ('link', models.CharField(max_length=200)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='headway.Course')),
            ],
        ),
    ]