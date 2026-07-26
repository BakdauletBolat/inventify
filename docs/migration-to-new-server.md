# Перенос inventify на новый сервер

Чеклист переезда с сервера `back` (46.226.123.91) на сервер маркетплейса
(86.107.45.177), где уже работают хостовый nginx и Nuxt-прод `kaynaravto.kz`.

## Вводные

|  | Старый (`back`) | Новый |
|---|---|---|
| IP | 46.226.123.91 | 86.107.45.177 |
| RAM | 3.8 ГБ | **1.9 ГБ, swap 0 и добавить нельзя** |
| CPU | — | 2 vCPU |
| Диск | 97 ГБ / занято 47 ГБ | 40 ГБ / свободно 32 ГБ |
| Проект | `/home/dev/inventify` | `/opt/inventify` |
| Что уже крутится | inventify | nginx (хост) + Nuxt `kaynaravto.kz` на :3000 |

**Переносим только дамп Postgres (~1.8 ГБ данных) и `.env`.**
Media (41 ГБ, 424 тыс. фото) не переносим — файлы уже в S3 PS.KZ, `USE_S3_MEDIA=1`.
На новом сервере их всё равно негде разместить.

**Ключевое ограничение:** без swap стек должен влезть в ~1.25 ГБ.
Под это сделан отдельный `docker-compose.prod.yml`.

**Образ собираем на старом сервере** и переносим готовым: на 1.9 ГБ без swap
`docker compose build` уходит в OOM (Alpine компилирует pillow и gevent из исходников).

---

## Этап 1. За сутки до переезда (днём, без даунтайма)

### 1.1. DNS

- [ ] Понизить TTL A-записи `back-kaynar.kz` до **300 секунд** (панель PS.KZ).
      Значение IP пока не трогаем. Менять TTL надо заранее — минимум за старый
      TTL до переезда, иначе провайдеры будут сидеть на прежнем кеше.
- [ ] `www.back-kaynar.kz` — это CNAME на `back-kaynar.kz`, отдельно переключать
      его не нужно, он поедет за основным доменом. TTL у CNAME тоже на 300.
- [ ] Проверить, покрывает ли текущий сертификат `www` (от этого зависит шаг 2.6):
      ```bash
      sudo openssl x509 -noout -text \
        -in /home/dev/inventify/docker/certbot/conf/live/back-kaynar.kz/fullchain.pem \
        | grep -A1 "Subject Alternative Name"
      ```

### 1.2. Освободить память на новом сервере

- [ ] Отключить ненужные на виртуалке сервисы (освобождает ~250 МБ):
      `fwupd` — обновление прошивок железа (сервер виртуальный),
      `multipathd` — SAN-диски с несколькими путями (диск один),
      `udisks2` — автомонтирование флешек (сервер без GUI).
      ```bash
      sudo systemctl disable --now fwupd multipathd udisks2
      # multipathd поднимается сокет-активацией, его надо гасить отдельно
      sudo systemctl disable --now multipathd.socket
      sudo systemctl disable --now fwupd-refresh.timer

      systemctl is-active fwupd multipathd udisks2 multipathd.socket   # все inactive
      free -h        # used должно упасть примерно с 774 Mi до ~520 Mi
      ```
      Откат: `sudo systemctl enable --now fwupd multipathd udisks2`
- [ ] Почистить протухшие сертификаты от снесённых проектов, чтобы
      `certbot renew` не ломился в Let's Encrypt по мёртвым доменам:
      ```bash
      sudo certbot certificates | grep -B2 EXPIRED     # посмотреть список
      sudo certbot delete --cert-name back-waffle.timebook.kz
      # ...и так для остальных EXPIRED, кроме kaynaravto.kz
      ```

### 1.3. Перенести проект на новый сервер

Переносим папку целиком через rsync, а не клонируем с GitHub: на новом сервере
нет доступа к репозиторию, и заводить там ssh-ключ в ночь переезда — лишняя
возня. Заодно приедут `.env` и история git.

- [ ] На **новом**: создать папки
      ```bash
      sudo mkdir -p /opt/inventify /var/www/inventify/staticfiles
      ```
- [ ] На **старом**: подтянуть актуальный код (контейнеры при этом не
      перезапускаются, прод продолжает работать)
      ```bash
      cd /home/dev/inventify
      git pull
      git log --oneline -3
      ```
- [ ] На **старом**: перенести папку (слеш в конце пути-источника обязателен)
      ```bash
      rsync -av \
        --exclude 'media/' \
        --exclude 'staticfiles/' \
        --exclude 'logs/' \
        --exclude '__pycache__/' \
        /home/dev/inventify/ root@86.107.45.177:/opt/inventify/
      ```
- [ ] На **новом**: проверить, что доехало
      ```bash
      cd /opt/inventify
      git branch --show-current            # in-8
      git log --oneline -3
      grep -E "USE_S3_MEDIA|DEBUG=" .env   # USE_S3_MEDIA=1, DEBUG=0
      ls docker-compose.prod.yml docker/host-nginx/back-kaynar.conf
      ```

### 1.4. Собрать образ на старом сервере и перенести

На **старом**:

- [ ] ```bash
      cd /home/dev/inventify
      git pull                       # подтянуть правки (tasks.py, celery.py, compose.prod)
      docker compose build web       # контейнеры при этом НЕ перезапускаются, прод живёт
      docker save inventify-web:latest | gzip -1 > /tmp/inventify-web.tgz
      ls -lh /tmp/inventify-web.tgz  # ~400-500 МБ
      ```
- [ ] Перекинуть на новый:
      ```bash
      scp /tmp/inventify-web.tgz root@86.107.45.177:/tmp/
      ```
      Если между серверами нет ssh — скачать себе на ноут и залить оттуда.

На **новом**:

- [ ] ```bash
      docker load < /tmp/inventify-web.tgz
      docker images | grep inventify        # должен появиться inventify-web:latest
      rm /tmp/inventify-web.tgz
      ```

### 1.5. Проверить `.env`

`.env` приехал вместе с rsync на шаге 1.3, править в нём ничего не надо:
`SQL_HOST=db` и `CELERY_BROKER_URL=redis://redis:...` — это имена
docker-сервисов, они на новом сервере те же.

- [ ] **`DEBUG=0`** — со старого сервера приезжает `DEBUG=1`, и так оставлять
      нельзя: при DEBUG подключается django-silk (профилирует каждый запрос
      и пишет его в БД), Django копит все SQL-запросы в памяти воркера,
      а страницы ошибок показывают настройки вместе с паролями и ключами S3.
      ```bash
      cd /opt/inventify
      sed -i 's/^DEBUG=1/DEBUG=0/' .env
      grep -E "^DEBUG=|^USE_S3_MEDIA=" .env      # DEBUG=0, USE_S3_MEDIA=1
      ```
      `DJANGO_ALLOWED_HOSTS` проверять не нужно: в `settings/base.py:15`
      стоит `ALLOWED_HOSTS = ['*']`, переменную из `.env` код не читает.

### 1.6. Репетиция (сильно рекомендую)

Прогнать весь Этап 2 на дневном дампе, кроме переключения DNS. Это покажет
реальное время восстановления базы и влезает ли стек в память — ночью уже
не будет неприятных сюрпризов. После репетиции:
```bash
cd /opt/inventify
docker compose -f docker-compose.prod.yml down -v      # -v удалит тестовую базу
```

---

## Этап 2. Ночь переезда (даунтайм ~40-60 минут)

### 2.1. Остановить запись на старом сервере

- [ ] ```bash
      cd /home/dev/inventify
      docker compose stop celery-worker flower web
      ```
      Celery останавливаем первым: пока он жив, ночные импорты Recar пишут в базу.
      `web` тоже гасим — иначе клиенты продолжат писать в базу, которую мы
      уже сдампили, и эти данные потеряются.

### 2.2. Снять дамп

Данные django-silk из дампа исключаются: профайлер писал каждый SQL-запрос,
пока прод работал с `DEBUG=1`, и накопил ~547 МБ (треть базы). На новом сервере
`DEBUG=0`, silk не подключается — эти записи там не нужны. Саму базу на старом
сервере это не меняет, данные просто не попадают в файл.

- [ ] ```bash
      docker compose exec -T db sh -c \
        'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc --no-owner --no-privileges \
           --exclude-table-data="silk_*"' \
        > /tmp/inventify.dump
      ls -lh /tmp/inventify.dump
      ```
- [ ] Перенести:
      ```bash
      scp /tmp/inventify.dump root@86.107.45.177:/opt/inventify/
      ```

### 2.3. Перенести сертификат (чтобы HTTPS не отвалился ни на минуту)

На старом сервере лежит валидный сертификат `back-kaynar.kz`. Копируем его,
и HTTPS на новом заработает сразу, ещё до переключения DNS.

- [ ] На **старом**:
      ```bash
      sudo tar czf /tmp/le-back-kaynar.tgz \
        -C /home/dev/inventify/docker/certbot/conf \
        live/back-kaynar.kz archive/back-kaynar.kz renewal/back-kaynar.kz.conf
      scp /tmp/le-back-kaynar.tgz root@86.107.45.177:/tmp/
      ```
- [ ] На **новом**:
      ```bash
      sudo tar xzf /tmp/le-back-kaynar.tgz -C /etc/letsencrypt/
      sudo certbot certificates | grep -A4 back-kaynar    # должен быть VALID
      ```

### 2.4. Поднять базу и восстановить дамп

На **новом**:

- [ ] ```bash
      cd /opt/inventify
      docker compose -f docker-compose.prod.yml up -d db
      docker compose -f docker-compose.prod.yml ps        # ждём healthy
      ```
- [ ] ```bash
      docker compose -f docker-compose.prod.yml exec -T db sh -c \
        'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --no-privileges -j 1' \
        < /opt/inventify/inventify.dump
      ```
      Это самая долгая часть — 20-40 минут (пересборка индексов на 2 vCPU).
      Одиночные `WARNING` про роли и расширения — нормально.
      `-j 1` намеренно: параллельное восстановление на 1.9 ГБ без swap уйдёт в OOM.

### 2.5. Поднять стек

- [ ] ```bash
      docker compose -f docker-compose.prod.yml up -d
      docker compose -f docker-compose.prod.yml ps
      ```
- [ ] Миграции и статика:
      ```bash
      docker compose -f docker-compose.prod.yml exec web \
        poetry run python manage.py migrate
      docker compose -f docker-compose.prod.yml exec web \
        poetry run python manage.py collectstatic --noinput
      ls /var/www/inventify/staticfiles | head
      ```
- [ ] Удалить задачу обновления цен из расписания. Она приехала вместе с дампом:
      `django_celery_beat` синхронизирует расписание в БД и **не удаляет** записи,
      убранные из кода.
      ```bash
      docker compose -f docker-compose.prod.yml exec web poetry run python manage.py shell -c \
        "from django_celery_beat.models import PeriodicTask; \
         print(PeriodicTask.objects.filter(task='apps.product.tasks.update_price').delete())"
      ```
- [ ] Проверить, что приложение отвечает:
      ```bash
      curl -si http://127.0.0.1:8000/api/ | head -5
      ```

### 2.6. Настроить nginx на хосте

- [ ] ```bash
      sudo cp /opt/inventify/docker/host-nginx/back-kaynar.conf \
              /etc/nginx/sites-available/back-kaynar.conf
      sudo ln -s /etc/nginx/sites-available/back-kaynar.conf /etc/nginx/sites-enabled/
      sudo nginx -t && sudo systemctl reload nginx
      ```
      `nginx -t` обязателен: ошибка в конфиге уронит и маркетплейс.
- [ ] Добавить HTTPS. Перенесённый сертификат покрывает оба имени
      (`back-kaynar.kz` и `www.back-kaynar.kz`), поэтому certbot просто
      перепишет конфиг, без обращения в Let's Encrypt и без проверки DNS:
      ```bash
      sudo certbot --nginx -d back-kaynar.kz -d www.back-kaynar.kz
      # выбрать "1: Attempt to reinstall this existing certificate"
      sudo nginx -t && sudo systemctl reload nginx
      ```
- [ ] Проверить HTTPS **до** переключения DNS, подменив резолв:
      ```bash
      curl -sik --resolve back-kaynar.kz:443:127.0.0.1 https://back-kaynar.kz/api/ | head -5
      curl -sik --resolve www.back-kaynar.kz:443:127.0.0.1 https://www.back-kaynar.kz/api/ | head -5
      ```
      Флаг `-k` тут только чтобы не спотыкаться о подмену резолва; ошибок про
      имя сертификата быть не должно — проверь, что в выводе нет `SSL:`-предупреждений.
- [ ] Убедиться, что маркетплейс не задет:
      ```bash
      curl -sI https://kaynaravto.kz | head -3
      ```

### 2.7. Переключить DNS

- [ ] Поменять A-запись `back-kaynar.kz`: `46.226.123.91` → `86.107.45.177`
- [ ] Дождаться (TTL 300, обычно 2-10 минут):
      ```bash
      dig +short back-kaynar.kz        # должно стать 86.107.45.177
      ```
- [ ] Проверить снаружи, уже без `--resolve`:
      ```bash
      curl -sI https://back-kaynar.kz/api/
      ```
- [ ] Проверить автопродление сертификата:
      ```bash
      sudo certbot renew --dry-run
      ```

### 2.8. Финальная проверка

- [ ] Память — самое важное:
      ```bash
      free -h                                   # available не должно быть < 150Mi
      docker stats --no-stream                  # ни один контейнер не у лимита
      ```
- [ ] Логин в админку, открыть список товаров, проверить что **фото грузятся**
      (URL должен быть на `object.pscloud.io`, не на `back-kaynar.kz/media/`).
- [ ] Celery жив и задачи зарегистрированы:
      ```bash
      docker compose -f docker-compose.prod.yml logs --tail=50 celery-worker
      docker compose -f docker-compose.prod.yml exec celery-worker \
        poetry run celery -A inventify inspect registered
      ```
- [ ] Старый сервер **не трогаем** ещё 3-7 дней — это план отката.

---

## Этап 3. Первая ночь после переезда

Импорты Recar идут с 00:00 до 03:00 — это главная нагрузка на память.

- [ ] Утром проверить, что никого не убил OOM:
      ```bash
      dmesg -T | grep -i "killed process"
      docker compose -f docker-compose.prod.yml ps       # нет ли перезапусков
      docker compose -f docker-compose.prod.yml logs --since 12h celery-worker | grep -iE "error|memory"
      ```
- [ ] Если что-то падало — первым делом снизить `mem_limit` у `web` до `320m`
      и убрать один воркер gunicorn (`--workers=1 --threads=6`).

---

## Откат

Пока старый сервер жив, откат занимает 5 минут:

1. Вернуть A-запись `back-kaynar.kz` на `46.226.123.91`
2. На старом: `cd /home/dev/inventify && docker compose start web celery-worker`

Данные, записанные на новом сервере после переезда, при откате потеряются —
поэтому откатываться имеет смысл только в первые часы.

---

## После переезда: чем деплоить

`make deploy` на новом сервере **работать не будет** — там `docker compose build`,
который на 1.9 ГБ без swap уходит в OOM. Пока старый сервер жив, можно собирать
на нём и переносить образ (шаг 1.4). Дальше нужен один из вариантов:

- **Сборка через GitHub Actions** в GHCR, на сервере только `docker compose pull && up -d`.
  Правильный вариант, требует настройки CI.
- **Сборка на ноутбуке** и пуш в Docker Hub:
  `docker buildx build --platform linux/amd64 -t <user>/inventify-web:latest --push .`
  Настройки не требует вообще, но на Apple Silicon сборка идёт через эмуляцию
  и занимает 15-30 минут.

Заодно стоит перевести Dockerfile на multi-stage и выбросить `gcc`/`build-base`
из финального образа — 1.34 ГБ ужмётся примерно втрое.

---

## Что уже изменено в коде под этот переезд

- `docker-compose.prod.yml` — конфиг под 1.9 ГБ: без nginx/certbot/flower,
  `mem_limit` на каждом сервисе, gunicorn `--preload --workers=2`,
  celery `--concurrency=1`, postgres с урезанными буферами,
  redis без персистентности (BGSAVE форкает процесс и удваивает память),
  порты БД и redis только на `127.0.0.1`.
- `docker/host-nginx/back-kaynar.conf` — конфиг для nginx на хосте.
- `apps/product/tasks.py` — `update_status_products` больше не держит в памяти
  четыре выборки Recar по 200 тыс. записей одновременно; обновление идёт порциями.
- `inventify/celery.py` — из расписания убрано обновление цен.
