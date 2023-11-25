# Generated by Django 4.1.7 on 2023-11-24 06:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('car', '0004_alter_modification_capacity'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='modification',
            options={'verbose_name': 'Тех характиристика автомобиля (Модификации)', 'verbose_name_plural': 'Тех характиристики автомобиля (Модификации)'},
        ),
        migrations.RemoveField(
            model_name='modification',
            name='engine',
        ),
        migrations.AddField(
            model_name='engine',
            name='modification',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='car.modification'),
        ),
    ]
