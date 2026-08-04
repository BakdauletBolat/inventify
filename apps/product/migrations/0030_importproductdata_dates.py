from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('product', '0029_merge_20260629_1423'),
    ]

    operations = [
        migrations.AddField(
            model_name='importproductdata',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Создан'),
        ),
        migrations.AddField(
            model_name='importproductdata',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Обновлён'),
        ),
        migrations.AlterField(
            model_name='importproductdata',
            name='product_id',
            field=models.IntegerField(db_index=True, verbose_name='Product ID'),
        ),
    ]
