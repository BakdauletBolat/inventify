from django.contrib import admin
from apps.product.models.Price import Price
from apps.product.models.Product import Product, ProductImage

admin.site.register(Price)
admin.site.register(Product)
admin.site.register(ProductImage)
