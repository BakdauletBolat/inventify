from django.core.exceptions import FieldError
from django.http import Http404
from rest_framework import exceptions
from rest_framework.exceptions import APIException, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    if isinstance(exc, APIException):
        message = exc.detail[0] if isinstance(exc.detail, list) else exc.detail
        response_data = {
            'code': exc.default_code,
            'detail': exc.default_detail,
            'message': message
        }
        return Response(response_data, status=exc.status_code)

    if isinstance(exc, Exception):
        if isinstance(exc, Http404):
            exc = exceptions.NotFound(*(exc.args))
        elif isinstance(exc, PermissionDenied):
            exc = exceptions.PermissionDenied(*(exc.args))
        elif isinstance(exc, (AssertionError, AttributeError, FieldError, ValueError)):
            return Response({
                'detail': exc.args
            }, status=500)
        else:
            return exception_handler(exc, context)

        message = exc.args[0] if isinstance(exc.args, (list, tuple)) else exc.args
        response_data = {
            'code': exc.default_code,
            'detail': exc.default_detail,
            'message': message
        }
        return Response(response_data, status=exc.status_code)

    return exception_handler(exc, context)
