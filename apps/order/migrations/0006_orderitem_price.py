# Generated by Django 4.1.7 on 2023-07-17 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_orderitem_quality'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='price',
            field=models.BigIntegerField(default=100),
        ),
    ]
