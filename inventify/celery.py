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
        'schedule': crontab(hour=1, minute=00)
    },

    'Обновление складов': {
        'task': 'apps.stock.tasks.import_warehouses_from_recar',
        'schedule': crontab(hour=00, minute=00)
    }
}

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.

# Load task modules from all registered Django apps.
# app.conf.timezone = settings.TIME_ZONE
