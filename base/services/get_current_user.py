from base.middlewares.RequestMiddleware import RequestMiddleware
from django.contrib.auth.models import AnonymousUser
from django.utils.functional import SimpleLazyObject


def get_current_user():
    thread_local = RequestMiddleware.thread_local
    if hasattr(thread_local, 'current_user'):
        user = thread_local.current_user
        return user
    else:
        return None
