"""Конфиг gunicorn для прода.

Нужен из-за связки `--preload` + drf-api-logger.

`drf_api_logger.start_logger_when_server_starts` на этапе импорта поднимает
фоновый поток `InsertLogIntoDatabase`, который раз в 10 секунд сбрасывает
накопленные запросы в БД. С `--preload` приложение импортируется в мастере,
поэтому поток стартует именно там, а потоки не переживают `fork` — в воркерах
его нет.

Последствия без этого хука:
  * запросы не попадают в `drf_api_logs` (сбрасываются только пачками по 50,
    когда срабатывает синхронная вставка в `put_log_data`);
  * очередь создана как `Queue(maxsize=50)`, а `put()` вызывается без таймаута,
    так что при конкурентных запросах поток-обработчик может заблокироваться
    на полной очереди и подвесить запрос.

Объект `LOGGER_THREAD` пересоздавать нельзя: middleware импортирует его по
значению (`from ... import LOGGER_THREAD`), и подмена в исходном модуле до него
не дойдёт. Поэтому переиспользуем тот же объект с его очередью и запускаем его
цикл разгребания в новом потоке.
"""


def post_fork(server, worker):
    import threading

    from drf_api_logger.start_logger_when_server_starts import LOGGER_THREAD

    if LOGGER_THREAD is None:
        return

    # Thread.start() у самого LOGGER_THREAD вызвать нельзя — после fork объект
    # считается уже запущенным и отдаёт RuntimeError.
    thread = threading.Thread(
        target=LOGGER_THREAD.start_queue_process,
        name='insert_log_into_database',
        daemon=True,
    )
    thread.start()
