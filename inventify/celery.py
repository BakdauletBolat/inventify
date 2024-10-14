import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventify.settings.dev')
app = Celery('inventify')
# Set the default Django settings module for the 'celery' program.

app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.update(result_extended=True)
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'Обновление продуктов и их модификаций': {
        'task': 'apps.car.tasks.import_car_data_recar',
        'schedule': crontab(hour=00, minute=00)
    },

    'Обновление складов': {
        'task': 'apps.stock.tasks.import_warehouses_from_recar',
        'schedule': crontab(hour=1, minute=00)
    },

    'Импорт моделей машины': {
        'task': 'apps.stock.tasks.create_car_models',
        'schedule': crontab(day_of_week=0, hour=0, minute=0),
    },

    'Импорт модификаций': {
        'task': 'apps.stock.tasks.import_modification_recar',
        'schedule': crontab(day_of_week=0, hour=1, minute=0),
    },

    'Обновление статуса продуктов': {
        'task': 'apps.product.tasks.update_status_products',
        'schedule': crontab(hour=00, minute=30)
    }
}

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.

# Load task modules from all registered Django apps.
# app.conf.timezone = settings.TIME_ZONE
