from django.db.models import F
from eav.models import Attribute

from apps.car.models.Modification import Modification
from apps.car.models.ModificationDetails import *


class GetFilters:

    def run(self):
        data = {}
        for attribute in Attribute.objects.all():
            if attribute.datatype == Attribute.TYPE_ENUM:
                data[attribute.name] = list(attribute.get_choices().values('id', name=F('value')))
            elif attribute.datatype == Attribute.TYPE_FLOAT:
                data[attribute.name] = list(attribute.value_set.values_list('value_float', flat=True).distinct())
            elif attribute.datatype == Attribute.TYPE_INT:
                data[attribute.name] = list(attribute.value_set.values_list('value_int', flat=True).distinct())
            elif attribute.datatype == Attribute.TYPE_TEXT:
                data[attribute.name] = list(attribute.value_set.values(name=F('value_text')))
        return data
