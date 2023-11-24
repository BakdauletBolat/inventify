from apps.product.repository import ProductRepository


class CreateProductAction:

    def __init__(self, data):
        self.data = data

    def run(self):
        product = ProductRepository.create(**self.data)
        return product


class UpdateProductAction:

    def __init__(self, data):
        self.data = data

    def run(self, instance):
        product = ProductRepository.update(instance, **self.data)
        return product
