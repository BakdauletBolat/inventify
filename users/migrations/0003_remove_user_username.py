# Generated by Django 4.1.7 on 2023-04-22 10:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_managers_alter_user_is_staff_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='username',
        ),
    ]
