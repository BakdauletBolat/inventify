# Generated by Django 4.2.14 on 2024-09-30 11:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0008_alter_order_address'),
        ('users', '0006_remove_address_street_address_postal_code_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Address',
        ),
    ]
