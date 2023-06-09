# Generated by Django 4.1.7 on 2023-04-23 11:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_rename_sdu_product_sku_alter_product_unique_together'),
        ('stock', '0002_stock_created_at_stock_updated_at_stock_warehouse_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stocks', to='product.product'),
        ),
    ]
