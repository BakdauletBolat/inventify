# Generated by Django 4.1.7 on 2024-02-27 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_order_client_order_comment_order_delivery_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_status',
            field=models.IntegerField(choices=[(1, 'В ожидании'), (2, 'Оплачен'), (3, 'Отклонен')], default=1),
        ),
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.IntegerField(choices=[(1, 'В процессе'), (2, 'Завершен'), (3, 'Отменен')], default=1),
        ),
        migrations.AddField(
            model_name='order',
            name='total',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
            preserve_default=False,
        ),
    ]
