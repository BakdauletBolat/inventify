from django.db import transaction
from rest_framework.response import Response
from rest_framework.views import APIView

from product.models import Product


@transaction.atomic
def handle_error_history_transaction(func):
    def handle_exception(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise e

    return handle_exception


# Create your views here.


class ProductTestView(APIView):

    @transaction.atomic
    def get(self, request):
        product = Product.objects.get(id=2)
        product.name = 'hello4'
        product.save()
        return Response({'status': 'ok'})



