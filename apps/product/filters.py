import django_filters
from django.db.models import OuterRef, Exists, Subquery, Q, QuerySet
from django.db.models.functions.text import Lower
from eav.models import Attribute, Value

from apps.car.models.Model import ModelCar
from apps.category.models import Category
from apps.product.models import Product
from apps.product.models.Price import Price


class ProductFilters(django_filters.FilterSet):
    price = django_filters.RangeFilter(field_name='price__cost')
    year_start = django_filters.NumberFilter(field_name='modification__modelCar__startDate__year', lookup_expr='gte')
    year_end = django_filters.NumberFilter(field_name='modification__modelCar__startDate__year', lookup_expr='lte')
    capacity = django_filters.RangeFilter(field_name='modification__capacity')
    body_type = django_filters.BaseInFilter(field_name='modification__bodyType')
    fuel_type = django_filters.BaseInFilter(field_name='modification__fuelType')
    gear_type = django_filters.BaseInFilter(field_name='modification__gearType')
    manufacturer = django_filters.BaseInFilter(field_name='modification__modelCar__manufacturer')

    class Meta:
        model = Product
        fields = ('__all__')


class DynamicProductFilterSet(django_filters.FilterSet):
    price = django_filters.RangeFilter(field_name='price__cost')
    category = django_filters.BaseInFilter(field_name='category__id', lookup_expr='in')
    search = django_filters.CharFilter(method='filter_by_product_or_category_name')

    class Meta:
        model = Product
        fields = []

    @staticmethod
    def filter_by_product_or_category_name(queryset: QuerySet, name, value):
        categories = Category.objects.filter(name__icontains=value)
        all_category = []
        for category in categories:
            all_category.extend(category.get_all_descendants())
        products = Product.objects.filter(category__in=all_category)
        product_queryset = queryset.filter(name__icontains=value)

        # Получаем списки ID из обоих queryset и объединяем их
        product_ids = list(product_queryset.values_list('id', flat=True))
        product_ids += list(products.values_list('id', flat=True))

        # Возвращаем объединённый queryset с помощью filter
        queryset = queryset.filter(id__in=product_ids)
        return queryset
    @classmethod
    def get_filters(cls):
        # Получаем существующие фильтры
        filters = super().get_filters()

        # Добавляем фильтры для EAV атрибутов
        for attribute in Attribute.objects.all():
            if attribute.datatype == Attribute.TYPE_OBJECT:
                if attribute.slug == 'modelCar':
                    filters['year_start'] = django_filters.NumberFilter(
                        method='filter_year_start'
                    )
                    filters['year_end'] = django_filters.NumberFilter(
                        method='filter_year_end'
                    )
                    filters['manufacturer'] = django_filters.BaseInFilter(
                        method='filter_manufacturer', lookup_expr='in'
                    )

                else:
                    filters[attribute.name] = django_filters.ModelChoiceFilter(
                        field_name=f'eav__{attribute.slug}', queryset=ModelCar.objects.all()
                    )
            elif attribute.datatype == Attribute.TYPE_ENUM:
                filters[attribute.name] = django_filters.ChoiceFilter(
                    field_name=f'eav__{attribute.slug}', choices=[
                        (choice.value, choice.value) for choice in attribute.enum_group.values.all()
                    ]
                )
            else:
                filters[attribute.name] = django_filters.CharFilter(
                    field_name=f'eav__{attribute.slug}', lookup_expr='icontains'
                )

        return filters

    @staticmethod
    def get_eav_subquery(model_car_ids):
        return Value.objects.filter(
            attribute__slug='modelCar',
            generic_value_id__in=model_car_ids,
            entity_id=OuterRef('pk')
        )

    def filter_year_start(self, queryset, name, value):
        modelCars = ModelCar.objects.filter(startDate__year__gte=value)
        eav_subquery = self.get_eav_subquery(modelCars.values_list('id', flat=True))
        return queryset.filter(Exists(eav_subquery))

    def filter_year_end(self, queryset, name, value):
        modelCars = ModelCar.objects.filter(endDate__year__lte=value)
        eav_subquery = self.get_eav_subquery(modelCars.values_list('id', flat=True))
        return queryset.filter(Exists(eav_subquery))

    def filter_manufacturer(self, queryset, name, value):
        modelCars = ModelCar.objects.filter(manufacturer_id__in=value)
        eav_subquery = self.get_eav_subquery(modelCars.values_list('id', flat=True))
        return queryset.filter(Exists(eav_subquery))

    def filter_by_latest_price(self, queryset, name, value):
        # Подзапрос для получения последней цены для каждого продукта
        latest_price_date = Price.objects.filter(product=OuterRef('pk')).order_by('-created_at').values('created_at')[
                            :1]

        # Подзапрос для получения стоимости последней цены на основе максимальной даты
        latest_price = Price.objects.filter(product=OuterRef('pk'), created_at=Subquery(latest_price_date)).values(
            'cost')[:1]

        # Аннотация для добавления последней цены в queryset
        queryset = queryset.annotate(latest_price=Subquery(latest_price))

        # Применяем фильтр диапазона к последней цене
        if value.start is not None:
            queryset = queryset.filter(latest_price__gte=value.start)
        if value.stop is not None:
            queryset = queryset.filter(latest_price__lte=value.stop)

        # Возвращаем только уникальные продукты
        return queryset.distinct()
