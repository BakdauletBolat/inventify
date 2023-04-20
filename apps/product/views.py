from django.db import transaction
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.product.models.Product import Product


class ProductTestView(APIView):

    @transaction.atomic
    def get(self, request):
        product = Product.objects.get(id=1)
        product.name = 'hello4'
        product.save(update_fields=['name'])
        return Response({'status': 'ok'})



