# Generated by Django 2.1.1 on 2021-03-11 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('examPortalApp', '0004_auto_20210305_1659'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='answer',
            name='answer_type',
        ),
        migrations.AddField(
            model_name='answer',
            name='answer_typed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='answer',
            name='status',
            field=models.CharField(default='u', max_length=2),
        ),
        migrations.AlterField(
            model_name='answer',
            name='answer_content',
            field=models.TextField(default=''),
        ),
    ]