# Generated by Django 2.1.1 on 2021-03-11 19:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('examPortalApp', '0005_auto_20210311_1439'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='answer',
            name='answer_typed',
        ),
    ]
