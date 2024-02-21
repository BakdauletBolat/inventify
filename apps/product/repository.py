from apps.product.models import Product
from apps.product.models.Price import Price
from apps.product.models.Product import ProductDetail
from base.repository import BaseRepository


class ProductRepository(BaseRepository):
    model = Product

    @classmethod
    def create(cls, **kwargs):
        product_detail = kwargs.pop('detail')
        categories = kwargs.pop('category')
        oem_codes = kwargs.pop('code')
        Price.objects.create(cost=kwargs.pop('price'))
        product = cls.model.objects.create(**kwargs)
        product.category.add(*categories)
        product.code.add(*oem_codes)

        product_detail['product'] = product
        ProductDetail.objects.create(**product_detail)
        return product

    @classmethod
    def update(cls, instance, **kwargs):
        price = kwargs.pop('price', None)
        details_data = kwargs.pop('detail', {})

        ProductDetail.objects.update_or_create(product=instance,
                                               defaults={**details_data},
                                               )
        if price is not None:
            Price.objects.get_or_create(product=instance, cost=price)

        super().update(instance, **kwargs)
        return instance
