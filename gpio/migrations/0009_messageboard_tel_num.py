# Generated by Django 5.0.6 on 2024-09-11 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gpio', '0008_remove_board_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='messageboard',
            name='tel_num',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
    ]
