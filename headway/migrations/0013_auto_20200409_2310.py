# Generated by Django 2.2.7 on 2020-04-09 21:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('headway', '0012_videoseries'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='videoseries',
            options={'verbose_name_plural': 'Video Series'},
        ),
        migrations.RenameField(
            model_name='testgrade',
            old_name='mark',
            new_name='marks',
        ),
        migrations.RemoveField(
            model_name='lecturer',
            name='courses',
        ),
        migrations.RemoveField(
            model_name='testgrade',
            name='test',
        ),
        migrations.AddField(
            model_name='grade',
            name='ca_grade',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='headway.TestGrade'),
        ),
        migrations.AddField(
            model_name='testgrade',
            name='ca_total',
            field=models.FloatField(default='20'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='testgrade',
            name='ca_value',
            field=models.FloatField(default=20.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='testgrade',
            name='course',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='headway.Course'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='testgrade',
            name='institution',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='headway.Institution'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='testgrade',
            name='lecturer',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='headway.Lecturer'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='testgrade',
            name='name',
            field=models.CharField(default='continuouse ass', max_length=100),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Test',
        ),
    ]
