from eav.models import Attribute
from rest_framework.exceptions import ValidationError, APIException

from apps.product.models import Product
from apps.product.models.Price import Price
from apps.product.models.Product import ProductDetail
from apps.stock.actions import StockAction
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
            try:
                attribute = Attribute.objects.get(name=attr_name)
                setattr(product.eav, attribute.slug, value)
            except Attribute.DoesNotExist:
                pass

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
        dest_warehouse = kwargs.pop('warehouse', {})
        ProductDetail.objects.update_or_create(product=instance,
                                               defaults={**details_data},
                                               )

        for attr_name, value in eav_data.items():

            try:
                attribute = Attribute.objects.get(name=attr_name)
                setattr(instance.eav, attribute.slug, value)
            except Attribute.DoesNotExist as e:
                pass

        try:
            instance.eav.validate_attributes()
        except Exception as e:
            raise ValidationError(detail=e.message)

        if price is not None:
            Price.objects.get_or_create(product=instance, cost=price)

        if dest_warehouse:
            warehouse = getattr(instance.stock.filter(quantity__gt=0).first(), 'warehouse')
            if warehouse:
                StockAction().move_product(instance, warehouse, dest_warehouse, 1)
            else:
                StockAction().process_ingoing(instance, dest_warehouse)

        super().update(instance, **kwargs)
        if len(codes):
            instance.code.set(codes)
        return instance
