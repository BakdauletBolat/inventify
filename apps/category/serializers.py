from rest_framework import serializers

from apps.category.models import Category


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True,
                                              help_text="Количество продуктов в категории")

    class Meta:
        model = Category
        fields = '__all__'


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CategoryTreeSerializer(serializers.ModelSerializer):
    children = RecursiveField(many=True, read_only=True, help_text="Дочерние категории")
    products_count = serializers.IntegerField(read_only=True,
                                              help_text="Количество продуктов в категории")

    class Meta:
        model = Category
        fields = ('id', 'name', 'parent', 'status', 'children', 'products_count')
