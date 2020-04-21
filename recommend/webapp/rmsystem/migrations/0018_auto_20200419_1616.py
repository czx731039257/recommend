# Generated by Django 2.1.4 on 2020-04-19 08:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rmsystem', '0017_auto_20200415_2251'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user_role',
            name='Role',
        ),
        migrations.RemoveField(
            model_name='user_role',
            name='User',
        ),
        migrations.AlterField(
            model_name='user',
            name='Cluster',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rmsystem.Cluster'),
        ),
        migrations.DeleteModel(
            name='User_Role',
        ),
    ]
