# Generated by Django 3.1.2 on 2021-05-27 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0008_remove_post_unlike_num'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='category',
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='comment',
            name='writer_category',
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='writer_category',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
