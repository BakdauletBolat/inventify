# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Inventify is a Django + DRF backend for auto-parts inventory and order management (Russian-language domain; comments, docstrings, and verbose names are in Russian). It integrates with the external **Recar** GraphQL API (`backend.recar.lt`) to import car models, modifications, engines, warehouses, products, and orders. Deployed under the `kaynaravto.kz` / `back-kaynar.kz` domain.

## Commands

Everything runs inside Docker via `poetry`. The `web` service is the Django app.

```bash
docker-compose up -d --build                                    # build & start full stack (web, db, redis, celery, nginx, flower)
docker-compose exec web poetry run python manage.py migrate     # apply migrations
docker-compose exec web poetry run python manage.py create_seed # seed data (note: README says create_seed; Makefile uses `seed`)
docker-compose exec web poetry run python manage.py <command>   # run any management command
docker-compose exec web poetry run python manage.py test        # run all tests
docker-compose exec web poetry run python manage.py test apps.stock.tests.SomeTest.test_x  # run a single test
```

The `Makefile` has shortcuts (`make migrate`, `make seed`, `make create_cars`, etc.) but note they are **stale** — they call `python manage` (missing `.py`) and omit `poetry run`. Prefer the explicit `docker-compose exec web poetry run python manage.py ...` form.

Local (non-Docker) dev settings module: `inventify.settings.dev` (just re-exports `base`). Settings live in `inventify/settings/base.py`. Env is loaded from `.env.dev` (see `load_dotenv` in `base.py`); other env files: `.env`, `.env.prod`, `.env.example`.

Infra ports: Postgres 5432, Redis 6381→6379, Flower 5557→5555, web 8000.

## Architecture

### Layered structure (per app)

Most apps under `apps/` follow a consistent layering. When adding behavior, place it in the matching layer rather than putting logic in views:

- **`views.py`** — DRF `ViewSet`s / `APIView`s. Thin; delegate to actions. Often pair a read `serializer_class` with a write/deserializer for input.
- **`actions.py`** — business logic and orchestration (e.g. `apps/stock/actions.py` `StockAction.move_product` wraps `transaction.atomic`). Actions compose repositories.
- **`repository.py`** — data-access layer. Subclass `base.repository.BaseRepository` (set `model = ...`); provides `get/create/update/delete/all`. **`BaseRepository.update` tracks changed fields** and stashes them on `instance._update_fields` before `save()` — preserve this when overriding.
- **`serializers.py`** / **`deserializers.py`** — DRF serialization, split read vs write where present.
- **`filters.py`** — `django-filter` `FilterSet`s used via `DjangoFilterBackend`.
- **`enums.py`** — choices (e.g. `OrderStatusChoices`, `MovementEnum`); base-wide ones in `base/enums.py` (`StatusEnum` with ACTIVE/DELETED — soft-delete is done by setting `status=DELETED`, not row deletion).
- **`tasks.py`** — Celery tasks (imports from Recar, status/price updates).

`base/` holds shared building blocks: `BaseModel` (`created_at`/`updated_at`), `BaseRepository`, `BaseAPIView`, `CustomPageNumberPagination`, `custom_exception_handler`, middlewares, and `RecarRequest`/`Request` in `base/requests.py` (Recar GraphQL client with cached access token).

### URL routing & API surface

All routes wired in `inventify/urls.py` under three prefixes:
- **`/api/admin/`** — staff/back-office endpoints. Guarded: see permissions below.
- **`/api/`** — general endpoints.
- **`/api/v2/`** — newer client-facing product endpoints.

The `product` app splits routes by audience: `apps/product/routes/admin.py` vs `apps/product/routes/client.py`.

### Auth & permissions

- Custom JWT auth, **not** simplejwt's default — `base/middlewares/BaseAuthMiddleware.CustomJWTAuthentication` manually decodes the `Bearer` token (`HS256`, `settings.SECRET_KEY`, `user_id` claim) and loads `users.User`. This is the configured `DEFAULT_AUTHENTICATION_CLASSES`.
- `AUTH_USER_MODEL = "users.User"`. Roles are M2M; role names come from `users.enums.RoleEnum`.
- Default permission is `inventify.permissions.InventifyAPIPermission`: any path starting with `/api/admin` requires `IsStaff` (a valid role or superuser); everything else is open. Role-specific classes (`IsManager`, `IsDirector`) also live in `inventify/permissions.py`.

### Audit history (two systems)

1. **Custom generic history** — `history/` app. `history.services.create_history.create_history(instance, created)` diffs old vs new field values and writes a `History` row (generic FK via `content_type`/`object_id`, `edits` JSON, acting user). It is wired per-model via Django signals — see `apps/product/models/Product.py` (`@receiver(post_save, sender=Product)` and an `m2m_changed` handler). To audit a new model, connect its signals the same way.
2. The acting user is resolved through thread-local state: `base/middlewares/RequestMiddleware.RequestMiddleware` stores `current_user` per request; `base/services/get_current_user.get_current_user()` reads it. `django-simple-history` is also installed.

### EAV (dynamic product attributes)

Products use **`django-eav2`** for dynamic attributes (engine, modelCar, enums, etc.). `apps/product/eav_serializer.py` (`ProductEAVSerializer`) handles read (`to_representation` walks `eav_values`, expanding `TYPE_OBJECT` like engine/modelCar into nested serializers) and write (`to_internal_value`). When touching product attributes, go through the EAV serializer rather than direct field access.

### Async / scheduled work

Celery app in `inventify/celery.py` (broker = Redis, result backend = `django-db`, beat scheduler = `django_celery_beat` DatabaseScheduler, timezone `Asia/Oral`). The `beat_schedule` defines nightly Recar sync jobs (car data, warehouses, models, modifications, engines, product status/price, orders). New periodic Recar imports go here as Celery tasks under each app's `tasks.py`.

### External integration

All Recar communication funnels through `base/requests.py` — it obtains and caches a GraphQL access token in Redis (`cache_key='access_token'`, ~3500s TTL). Reuse this client for new Recar calls instead of issuing raw `requests`.

## Conventions

- Domain text (docstrings, `verbose_name`, error messages) is **Russian**. Match the surrounding language.
- Soft-delete via `status=StatusEnum.DELETED` and filter on `status=ACTIVE`, rather than deleting rows.
- Keep views thin: input validation in (de)serializers, business logic in `actions.py`, queries in `repository.py`.
- API docs are served via `drf-yasg` (`inventify/yasg.py`), request/response logging via `drf-api-logger`.
