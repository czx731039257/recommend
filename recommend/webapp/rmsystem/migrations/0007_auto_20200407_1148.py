# Generated by Django 2.1.4 on 2020-04-07 03:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rmsystem', '0006_genres_name_ch'),
    ]

    operations = [
        migrations.RenameField(
            model_name='genres',
            old_name='name',
            new_name='name_en',
        ),
    ]
