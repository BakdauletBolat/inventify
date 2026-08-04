from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='RecarRequestLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operation_name', models.CharField(blank=True, db_index=True, max_length=255, verbose_name='Операция')),
                ('query', models.TextField(blank=True, verbose_name='GraphQL-запрос')),
                ('variables', models.JSONField(blank=True, null=True, verbose_name='Переменные')),
                ('response', models.JSONField(blank=True, null=True, verbose_name='Ответ')),
                ('status_code', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='HTTP-статус')),
                ('duration_ms', models.PositiveIntegerField(blank=True, null=True, verbose_name='Длительность, мс')),
                ('error', models.TextField(blank=True, verbose_name='Ошибка')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Время запроса')),
            ],
            options={
                'verbose_name': 'Запрос в Recar',
                'verbose_name_plural': 'Запросы в Recar',
                'ordering': ('-id',),
            },
        ),
    ]
