# Generated by Django 4.2 on 2023-05-11 17:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0020_usercategory_post_user_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='user_category',
        ),
        migrations.DeleteModel(
            name='UserCategory',
        ),
    ]
