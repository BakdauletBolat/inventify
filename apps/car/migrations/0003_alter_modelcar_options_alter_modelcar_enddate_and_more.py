# Generated by Django 4.1.7 on 2023-11-23 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('car', '0002_modification'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='modelcar',
            options={'verbose_name': 'Модель автомобиля', 'verbose_name_plural': 'Модель автомобиля'},
        ),
        migrations.AlterField(
            model_name='modelcar',
            name='endDate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='modelcar',
            name='startDate',
            field=models.DateField(blank=True, null=True),
        ),
    ]