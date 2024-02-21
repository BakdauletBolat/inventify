from apps.car.models.Modification import Modification
from apps.car.models.ModificationDetails import *


class GetFilters:

    def run(self):
        return {
            "capacities": list(Modification.objects.values('id', 'capacity').distinct()),
            "body_types": list(BodyType.objects.values('id', 'name')),
            "fuel_types": list(FuelType.objects.values('id', 'name')),
            "drive_types": list(DriveType.objects.values('id', 'name')),
            "gear_types": list(GearType.objects.values('id', 'name')),
            "colors": list(ColorType.objects.values('id', 'name')),
            "powers": list(Modification.objects.values('id', 'power').distinct()),
        }