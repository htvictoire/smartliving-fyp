# Generated by Django 5.0.6 on 2024-09-15 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gpio', '0011_pins_today_limit_reached_alter_pins_consom_max'),
    ]

    operations = [
        migrations.AlterField(
            model_name='places',
            name='description',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
