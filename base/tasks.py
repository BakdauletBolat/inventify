from datetime import timedelta

from celery import shared_task
from django.utils import timezone

# Размер чанка при удалении — чтобы не держать долгий lock на таблице
DELETE_CHUNK_SIZE = 10000


def _delete_in_chunks(queryset, chunk_size=DELETE_CHUNK_SIZE):
    """Удаляет записи queryset чанками по pk, возвращает число удалённых строк."""
    model = queryset.model
    total = 0
    while True:
        pks = list(queryset.values_list('pk', flat=True)[:chunk_size])
        if not pks:
            return total
        deleted, _ = model.objects.filter(pk__in=pks).delete()
        total += deleted


@shared_task
def clean_drf_api_logs():
    """
    Ретенция логов drf-api-logger (таблица drf_api_logs):
    записи со status_code >= 500 храним 30 дней, все остальные — 7 дней.
    """
    from drf_api_logger.models import APILogsModel

    now = timezone.now()
    deleted_errors = _delete_in_chunks(
        APILogsModel.objects.filter(
            status_code__gte=500,
            added_on__lt=now - timedelta(days=30),
        )
    )
    deleted_other = _delete_in_chunks(
        APILogsModel.objects.filter(
            status_code__lt=500,
            added_on__lt=now - timedelta(days=7),
        )
    )
    return {'deleted_5xx': deleted_errors, 'deleted_other': deleted_other}
