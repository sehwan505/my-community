# Generated by Django 3.1.2 on 2021-05-27 07:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0007_auto_20210525_2152'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='unlike_num',
        ),
    ]
