# Generated by Django 5.0.6 on 2024-09-10 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gpio', '0005_remove_pins_fav'),
    ]

    operations = [
        migrations.AddField(
            model_name='pins',
            name='consom_max',
            field=models.FloatField(default=1000.0),
        ),
        migrations.AddField(
            model_name='pins',
            name='power',
            field=models.FloatField(default=0.0),
        ),
    ]
