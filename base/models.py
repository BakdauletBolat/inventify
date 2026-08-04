from django.db import models


# Create your models here.
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class RecarRequestLog(models.Model):
    """Лог обращений к Recar GraphQL API.

    Пишется в base.requests.Request.post — единственной точке, через которую
    идут интеграционные запросы, поэтому покрывает импорт товаров, заказов,
    модификаций и складов. Нужен, чтобы видеть, что именно мы отправили
    в Recar и что он ответил: по одному сохранённому снапшоту причину
    расхождения данных не установить.

    Большие ответы (например FetchParts на 200 000 записей) не сохраняются
    целиком — вместо тела пишется отметка об усечении, см.
    base.services.recar_request_log.
    """

    operation_name = models.CharField('Операция', max_length=255, blank=True, db_index=True)
    query = models.TextField('GraphQL-запрос', blank=True)
    variables = models.JSONField('Переменные', null=True, blank=True)
    response = models.JSONField('Ответ', null=True, blank=True)
    status_code = models.PositiveSmallIntegerField('HTTP-статус', null=True, blank=True)
    duration_ms = models.PositiveIntegerField('Длительность, мс', null=True, blank=True)
    error = models.TextField('Ошибка', blank=True)
    created_at = models.DateTimeField('Время запроса', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Запрос в Recar'
        verbose_name_plural = 'Запросы в Recar'
        ordering = ('-id',)

    def __str__(self):
        return f'{self.operation_name} ({self.created_at:%d.%m.%Y %H:%M:%S})'
