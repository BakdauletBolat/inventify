import json
import logging

from django.conf import settings

logger = logging.getLogger('django')

# Операции, у которых в переменных и ответе лежат учётные данные и токены
SENSITIVE_OPERATIONS = ('ObtainTokens', 'RefreshTokens')
SENSITIVE_KEYS = ('password', 'accessToken', 'refreshToken', 'idToken')
MASK = '***'

# Ответ FetchParts на 200 000 записей — десятки мегабайт; такое в БД не пишем
DEFAULT_MAX_RESPONSE_BYTES = 100 * 1024
PREVIEW_LENGTH = 5000
ERROR_PREVIEW_LENGTH = 2000


def is_enabled() -> bool:
    return getattr(settings, 'RECAR_REQUEST_LOG_ENABLED', True)


def _max_response_bytes() -> int:
    return getattr(settings, 'RECAR_REQUEST_LOG_MAX_RESPONSE_BYTES', DEFAULT_MAX_RESPONSE_BYTES)


def _mask_keys(value):
    """Рекурсивно заменяет значения чувствительных ключей на маску."""
    if isinstance(value, dict):
        return {
            key: MASK if key in SENSITIVE_KEYS else _mask_keys(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_mask_keys(item) for item in value]
    return value


def prepare_variables(operation_name: str, variables):
    if operation_name in SENSITIVE_OPERATIONS:
        return _mask_keys(variables)
    return variables


def prepare_response(operation_name: str, response):
    """Готовит тело ответа к записи: маскирует токены и усекает большие ответы."""
    if response is None:
        return None

    if operation_name in SENSITIVE_OPERATIONS:
        response = _mask_keys(response)

    dumped = json.dumps(response, ensure_ascii=False, default=str)
    size = len(dumped.encode('utf-8'))
    if size > _max_response_bytes():
        return {
            '_truncated': True,
            'size': size,
            'preview': dumped[:PREVIEW_LENGTH],
        }
    return response


def log_request(body: dict, response=None, status_code=None, duration_ms=None, error: str = ''):
    """Пишет строку в RecarRequestLog.

    Никогда не бросает исключений: сбой логирования не должен ломать сам
    запрос в Recar.
    """
    if not is_enabled():
        return None

    try:
        from base.models import RecarRequestLog

        body = body or {}
        operation_name = body.get('operationName') or ''
        return RecarRequestLog.objects.create(
            operation_name=operation_name,
            query=body.get('query') or '',
            variables=prepare_variables(operation_name, body.get('variables')),
            response=prepare_response(operation_name, response),
            status_code=status_code,
            duration_ms=duration_ms,
            error=(error or '')[:ERROR_PREVIEW_LENGTH],
        )
    except Exception as exc:  # noqa: BLE001 — логирование не должно ломать интеграцию
        logger.error(f'Не удалось записать лог запроса в Recar: {exc}')
        return None
