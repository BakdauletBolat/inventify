# Generated by Django 4.1.7 on 2024-02-28 04:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('handbook', '0003_alter_city_uid_alter_country_uid'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Address',
        ),
    ]