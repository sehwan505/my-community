# Generated by Django 3.1.2 on 2021-05-13 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0002_remove_post_betting'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='section',
            field=models.PositiveIntegerField(default=0),
        ),
    ]