# Generated by Django 5.0.6 on 2024-09-07 18:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gpio', '0004_alter_pins_gpio'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pins',
            name='fav',
        ),
    ]
