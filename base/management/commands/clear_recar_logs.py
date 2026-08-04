from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from base.models import RecarRequestLog
from base.tasks import _delete_in_chunks

DEFAULT_RETENTION_DAYS = 14


class Command(BaseCommand):
    help = 'Удаляет логи запросов в Recar старше указанного количества дней'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=getattr(settings, 'RECAR_REQUEST_LOG_RETENTION_DAYS', DEFAULT_RETENTION_DAYS),
            help='Сколько дней хранить логи (по умолчанию из настроек)',
        )

    def handle(self, *args, **options):
        days = options['days']
        border = timezone.now() - timedelta(days=days)
        deleted = _delete_in_chunks(RecarRequestLog.objects.filter(created_at__lt=border))
        self.stdout.write(self.style.SUCCESS(f'Удалено логов Recar: {deleted} (старше {days} дн.)'))
