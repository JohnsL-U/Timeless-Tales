# Generated by Django 4.2 on 2023-05-06 13:10

from django.db import migrations
import django_quill.fields


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0014_remove_post_video'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='description',
            field=django_quill.fields.QuillField(),
        ),
    ]
