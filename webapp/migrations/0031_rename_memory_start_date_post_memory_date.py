# Generated by Django 4.2 on 2023-05-28 19:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0030_post_date_range'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='memory_start_date',
            new_name='memory_date',
        ),
    ]
