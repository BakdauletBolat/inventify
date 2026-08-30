COMPOSE = docker compose
COMPOSE_PROD = docker compose -f docker-compose.prod.yml

# ============================================================
# Деплой на прод: подтянуть код и готовый образ, поднять, почистить
#
# Образ собирается в GitHub Actions и лежит в ghcr — на прод-сервере
# 1.9 ГБ RAM без swap, `docker compose build` там уходит в OOM.
# ============================================================

.PHONY: deploy
deploy:                ## git pull -> pull образа -> up -d -> migrate -> clean
	git pull
	$(COMPOSE_PROD) pull
	$(COMPOSE_PROD) up -d
	$(MAKE) migrate-prod
	$(MAKE) clean

.PHONY: migrate-prod
migrate-prod:
	$(COMPOSE_PROD) exec web poetry run python manage.py migrate
	$(COMPOSE_PROD) exec web poetry run python manage.py collectstatic --noinput

# Откат на предыдущий образ: посмотреть теги и запустить нужный
.PHONY: rollback-list
rollback-list:         ## показать скачанные образы приложения
	docker images ghcr.io/bakdauletbolat/inventify --format '{{.Tag}}\t{{.CreatedSince}}'

# Безопасная чистка. Не трогает БД, фото (media_volume) и статику.
# Запускается автоматически после каждого deploy.
.PHONY: clean
clean:                 ## journald + неиспользуемые образы + build-кэш + apt-кэш
	-sudo journalctl --vacuum-size=300M
	-docker image prune -a -f
	-docker builder prune -f
	-sudo apt-get clean
	@echo "Чистка завершена (БД, фото и статика не затронуты)."

# ============================================================
# Разовая настройка лимитов логов (чтобы диск больше не забивался).
# Запустить ОДИН раз на проде: make setup-logs
# ============================================================

.PHONY: setup-logs
setup-logs:            ## лимит journald 300M + лимит логов контейнеров 50m x 3
	# journald -> 300M
	sudo sed -i 's/^#\?SystemMaxUse=.*/SystemMaxUse=300M/' /etc/systemd/journald.conf
	grep -qE '^SystemMaxUse=' /etc/systemd/journald.conf || echo 'SystemMaxUse=300M' | sudo tee -a /etc/systemd/journald.conf
	sudo systemctl restart systemd-journald
	# docker log-opts -> 50m x 3 (только если daemon.json ещё нет)
	@if [ -f /etc/docker/daemon.json ]; then \
		echo "!! /etc/docker/daemon.json уже есть — не трогаю. Добавь log-opts вручную."; \
	else \
		printf '{\n  "log-driver": "json-file",\n  "log-opts": { "max-size": "50m", "max-file": "3" }\n}\n' | sudo tee /etc/docker/daemon.json; \
		sudo systemctl restart docker; \
		echo "daemon.json создан. Пересоздай контейнеры: make recreate"; \
	fi
	@echo "Лимиты логов настроены."

# Пересоздать контейнеры, чтобы подхватили лимит логов Docker
.PHONY: recreate
recreate:              ## up -d --force-recreate (применить лимит логов к контейнерам)
	$(COMPOSE) up -d --force-recreate

# ============================================================
# Management-команды приложения
# ============================================================

.PHONY: migrate
migrate:
	$(COMPOSE) exec web poetry run python manage.py migrate

.PHONY: seed
seed:
	$(COMPOSE) exec web poetry run python manage.py seed
	$(COMPOSE) exec web poetry run python manage.py import_warehouse

.PHONY: create_category
create_category:
	$(COMPOSE) exec web poetry run python manage.py create_category

.PHONY: create_cars
create_cars:
	$(COMPOSE) exec web poetry run python manage.py create_car_models

.PHONY: create_modifications
create_modifications:
	$(COMPOSE) exec web poetry run python manage.py import_modifications

.PHONY: create_engines
create_engines:
	$(COMPOSE) exec web poetry run python manage.py create_engines
