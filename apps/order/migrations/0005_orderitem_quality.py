# Generated by Django 4.1.7 on 2023-07-17 13:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0006_stockreceipt'),
        ('order', '0004_alter_orderitem_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='quality',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='stock.quality'),
            preserve_default=False,
        ),
    ]
