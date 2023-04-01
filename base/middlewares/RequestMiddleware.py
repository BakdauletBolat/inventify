import threading
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser


class RequestMiddleware(MiddlewareMixin):
    thread_local = threading.local()

    def process_request(self, request):
        RequestMiddleware.thread_local.current_user = None
        if request.user != AnonymousUser:
            RequestMiddleware.thread_local.current_user = request.user
