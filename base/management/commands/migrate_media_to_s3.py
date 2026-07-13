import mimetypes
import os

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import FileField


def _human_size(num_bytes):
    size = float(num_bytes)
    for unit in ('Б', 'КБ', 'МБ', 'ГБ', 'ТБ'):
        if size < 1024 or unit == 'ТБ':
            return f'{size:.1f} {unit}'
        size /= 1024


class Command(BaseCommand):
    help = (
        'Разовая загрузка всех локальных media-файлов в S3-бакет (PS.KZ). '
        'Идемпотентна: файлы, уже существующие в бакете с тем же размером, пропускаются. '
        'Значения путей в БД не меняются.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать список файлов и общий объём без загрузки в бакет',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        media_root = str(settings.MEDIA_ROOT)

        if not os.path.isdir(media_root):
            raise CommandError(f'MEDIA_ROOT не найден: {media_root}')

        # 1. Пути файлов, привязанных к моделям (значения FileField/ImageField в БД)
        model_paths = self._collect_model_paths()
        self.stdout.write(f'Путей в БД (FileField/ImageField): {len(model_paths)}')

        # 2. Файлы на диске: разделяем на привязанные к моделям и осиротевшие
        bound_files = []    # (relative_key, local_path, size)
        orphan_files = []
        for dirpath, _, filenames in os.walk(media_root):
            for filename in filenames:
                local_path = os.path.join(dirpath, filename)
                rel = os.path.relpath(local_path, media_root)
                key = rel.replace(os.sep, '/')
                try:
                    size = os.path.getsize(local_path)
                except OSError:
                    continue
                if key in model_paths:
                    bound_files.append((key, local_path, size))
                else:
                    orphan_files.append((key, local_path, size))

        missing_in_fs = model_paths - {key for key, _, _ in bound_files}

        bound_size = sum(size for _, _, size in bound_files)
        orphan_size = sum(size for _, _, size in orphan_files)
        self.stdout.write(
            f'Файлов моделей на диске: {len(bound_files)} ({_human_size(bound_size)}); '
            f'осиротевших (без записи в БД): {len(orphan_files)} ({_human_size(orphan_size)}); '
            f'в БД есть, на диске нет: {len(missing_in_fs)}'
        )

        if dry_run:
            self._report_dry_run(bound_files, orphan_files, missing_in_fs)
            return

        client = self._build_client()
        bucket = settings.AWS_STORAGE_BUCKET_NAME

        errors = []
        stats = {'uploaded': 0, 'uploaded_bytes': 0, 'skipped': 0, 'processed': 0}
        total = len(bound_files) + len(orphan_files)

        self.stdout.write(self.style.MIGRATE_HEADING('Загрузка файлов моделей:'))
        self._upload_batch(client, bucket, bound_files, total, stats, errors)

        self.stdout.write(self.style.MIGRATE_HEADING('Загрузка осиротевших файлов:'))
        self._upload_batch(client, bucket, orphan_files, total, stats, errors)

        self.stdout.write(self.style.SUCCESS(
            f'Готово. Загружено: {stats["uploaded"]} ({_human_size(stats["uploaded_bytes"])}), '
            f'пропущено (уже в бакете): {stats["skipped"]}, ошибок: {len(errors)}'
        ))
        if missing_in_fs:
            self.stdout.write(self.style.WARNING(
                f'Записей в БД без файла на диске: {len(missing_in_fs)} — они не загружены:'
            ))
            for key in sorted(missing_in_fs):
                self.stdout.write(f'  {key}')
        if errors:
            self.stdout.write(self.style.ERROR('Ошибки загрузки:'))
            for key, exc in errors:
                self.stdout.write(f'  {key}: {exc}')

    def _collect_model_paths(self):
        """Собирает относительные пути всех непустых FileField/ImageField по всем моделям."""
        paths = set()
        for model in apps.get_models():
            file_fields = [
                field.name for field in model._meta.get_fields()
                if isinstance(field, FileField)
            ]
            for field_name in file_fields:
                queryset = (
                    model._default_manager
                    .exclude(**{field_name: ''})
                    .exclude(**{f'{field_name}__isnull': True})
                    .values_list(field_name, flat=True)
                )
                for value in queryset.iterator():
                    if value:
                        paths.add(str(value).replace(os.sep, '/'))
        return paths

    def _build_client(self):
        import boto3
        from botocore.config import Config

        if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
            raise CommandError(
                'Не заданы AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY в окружении'
            )
        return boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=Config(s3={'addressing_style': settings.AWS_S3_ADDRESSING_STYLE}),
        )

    def _upload_batch(self, client, bucket, files, total, stats, errors):
        from botocore.exceptions import ClientError

        for key, local_path, size in files:
            stats['processed'] += 1
            try:
                if self._exists_with_same_size(client, bucket, key, size):
                    stats['skipped'] += 1
                else:
                    content_type = mimetypes.guess_type(local_path)[0] or 'application/octet-stream'
                    # upload_file читает файл потоково (multipart для больших файлов)
                    client.upload_file(
                        local_path, bucket, key,
                        ExtraArgs={'ACL': 'public-read', 'ContentType': content_type},
                    )
                    stats['uploaded'] += 1
                    stats['uploaded_bytes'] += size
            except (ClientError, OSError) as exc:
                errors.append((key, exc))

            if stats['processed'] % 100 == 0 or stats['processed'] == total:
                self.stdout.write(
                    f'  {stats["processed"]}/{total}: загружено {stats["uploaded"]} '
                    f'({_human_size(stats["uploaded_bytes"])}), пропущено {stats["skipped"]}, '
                    f'ошибок {len(errors)}'
                )

    @staticmethod
    def _exists_with_same_size(client, bucket, key, size):
        from botocore.exceptions import ClientError

        try:
            head = client.head_object(Bucket=bucket, Key=key)
        except ClientError as exc:
            if exc.response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 404:
                return False
            if exc.response.get('Error', {}).get('Code') in ('404', 'NoSuchKey', 'NotFound'):
                return False
            raise
        return head.get('ContentLength') == size

    def _report_dry_run(self, bound_files, orphan_files, missing_in_fs):
        self.stdout.write(self.style.MIGRATE_HEADING('[dry-run] Файлы моделей:'))
        for key, _, size in bound_files:
            self.stdout.write(f'  {key} ({_human_size(size)})')
        self.stdout.write(self.style.MIGRATE_HEADING('[dry-run] Осиротевшие файлы:'))
        for key, _, size in orphan_files:
            self.stdout.write(f'  {key} ({_human_size(size)})')
        if missing_in_fs:
            self.stdout.write(self.style.WARNING('[dry-run] В БД есть, на диске нет:'))
            for key in sorted(missing_in_fs):
                self.stdout.write(f'  {key}')
        total_size = sum(s for _, _, s in bound_files) + sum(s for _, _, s in orphan_files)
        total_count = len(bound_files) + len(orphan_files)
        self.stdout.write(self.style.SUCCESS(
            f'[dry-run] Итого к загрузке: {total_count} файлов, {_human_size(total_size)}. '
            'Загрузка не выполнялась.'
        ))
