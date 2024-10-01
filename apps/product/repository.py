from eav.models import Attribute
from rest_framework.exceptions import ValidationError, APIException

from apps.product.models import Product
from apps.product.models.Price import Price
from apps.product.models.Product import ProductDetail
from base.repository import BaseRepository


class ProductRepository(BaseRepository):
    model = Product

    @classmethod
    def create(cls, **kwargs):
        product_detail = kwargs.pop('detail')
        oem_codes = kwargs.pop('code', [])
        if kwargs.get('price', None):
            Price.objects.create(cost=kwargs.pop('price', 0))
        eav_data = kwargs.pop('eav_attributes', {})

        product = cls.model.objects.create(**kwargs)
        product.code.add(*oem_codes)

        product_detail['product'] = product
        for attr_name, value in eav_data.items():

            attribute = Attribute.objects.get(name=attr_name)
            setattr(product.eav, attribute.slug, value)

        try:
            product.eav.validate_attributes()
        except Exception as e:
            raise ValidationError(detail=e.message)

        product.save()
        ProductDetail.objects.create(**product_detail)
        return product

    @classmethod
    def update(cls, instance, **kwargs):
        price = kwargs.pop('price', None)
        details_data = kwargs.pop('detail', {})
        codes = kwargs.pop('code', [])
        eav_data = kwargs.pop('eav_attributes', {})
        ProductDetail.objects.update_or_create(product=instance,
                                               defaults={**details_data},
                                               )

        for attr_name, value in eav_data.items():

            attribute = Attribute.objects.get(name=attr_name)
            setattr(instance.eav, attribute.slug, value)

        try:
            instance.eav.validate_attributes()
        except Exception as e:
            raise ValidationError(detail=e.message)

        if price is not None:
            Price.objects.get_or_create(product=instance, cost=price)

        super().update(instance, **kwargs)
        instance.code.set(codes)
        return instance
