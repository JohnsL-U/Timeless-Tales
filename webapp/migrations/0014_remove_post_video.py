# Generated by Django 3.2.18 on 2023-04-26 21:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0013_alter_userprofile_profile_pic'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='video',
        ),
    ]
