# Generated by Django 4.2 on 2023-05-28 22:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0032_post_end_year'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='memory_date',
            new_name='date',
        ),
        migrations.RenameField(
            model_name='post',
            old_name='memory_end_date',
            new_name='end_date',
        ),
        migrations.RenameField(
            model_name='post',
            old_name='date_range',
            new_name='include_interval',
        ),
    ]
