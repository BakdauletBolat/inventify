# Generated by Django 4.1.7 on 2023-04-26 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0004_remove_stockhistory_product_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockhistory',
            name='quantity_before',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
