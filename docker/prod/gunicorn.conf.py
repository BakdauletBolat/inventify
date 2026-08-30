"""Конфиг gunicorn для прода.

Нужен из-за связки `--preload` + drf-api-logger.

Библиотека поднимает фоновый поток `InsertLogIntoDatabase`, который раз в
`DRF_LOGGER_INTERVAL` секунд пачками сбрасывает накопленные запросы в БД.
Поток стартует при инициализации приложения, а с `--preload` это происходит
в мастер-процессе gunicorn — потоки же не переживают `fork`, поэтому в
воркерах его нет.

Без этого хука очередь растёт в памяти воркера и попадает в БД только при
его перезапуске (`--max-requests`), когда срабатывает `atexit`-обработчик.
То есть логи запросов и теряются, и приходят с большой задержкой.

Хук переиспользует уже созданный объект потока, а не делает новый: во-первых,
именно в его очередь пишет middleware; во-вторых, `InsertLogIntoDatabase.__init__`
вешает свои обработчики `SIGINT`/`SIGTERM`, а лезть в сигналы воркера незачем.
`Thread.start()` у самого объекта вызвать нельзя — после `fork` он считается
уже запущенным и отдаёт `RuntimeError`, поэтому его цикл запускается в новом
потоке.

Расположение `LOGGER_THREAD` зависит от версии библиотеки, поэтому проверяются
оба варианта. Любая ошибка гасится в лог: сбор логов необязателен и не должен
мешать воркеру подняться.
"""

LOG_THREAD_NAME = 'insert_log_into_database'


def _find_logger_thread():
    """Объект фонового потока drf-api-logger или None."""
    # 1.4.x — поток создаётся в AppConfig.ready() и лежит в drf_api_logger.apps
    try:
        from drf_api_logger import apps as logger_apps
        thread = getattr(logger_apps, 'LOGGER_THREAD', None)
        if thread is not None:
            return thread
    except ImportError:
        pass

    # 1.1.x — поток создаётся на импорте отдельного модуля
    try:
        from drf_api_logger import start_logger_when_server_starts as logger_start
        return getattr(logger_start, 'LOGGER_THREAD', None)
    except ImportError:
        return None


def post_fork(server, worker):
    try:
        import threading

        logger_thread = _find_logger_thread()
        if logger_thread is None:
            return

        # На случай запуска без --preload: поток уже живой, второй не нужен
        for thread in threading.enumerate():
            if thread.name == LOG_THREAD_NAME and thread.is_alive():
                return

        threading.Thread(
            target=logger_thread.start_queue_process,
            name=LOG_THREAD_NAME,
            daemon=True,
        ).start()
    except Exception as exc:
        worker.log.warning(
            'drf-api-logger: не удалось перезапустить поток записи логов: %s', exc
        )
