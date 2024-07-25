from apps.car.helpers import *
from apps.car.models.Modification import Modification
from base.requests import RecarRequest


class ImportModification:

    def __init__(self):
        self.body_types = dict(BodyTypeEnum.get_values())
        self.drive_types = dict(DriveTypeEnum.get_values())
        self.fuel_types = dict(FuelTypeEnum.get_values())
        self.gear_types = dict(GearTypeEnum.get_values())

    def run(self, car_model_id: int) -> None:
        recar_request = RecarRequest()

        modifications = []
        modifications_data = recar_request.get_modifications(modelId=car_model_id)
        for modification in modifications_data:
            modifications.append(
                Modification(id=modification['id'],
                             modelCar_id=int(modification['modelId']),
                             bodyType_id=self.body_types.get(modification['bodyType']),
                             driveType_id=self.drive_types.get(modification['driveType']),
                             fuelType_id=self.fuel_types.get(modification['fuelType']),
                             gearType_id=self.gear_types.get(modification['gearType']),
                             power=modification['power'],
                             numberOfCycle=modification['numOfCyl'],
                             numberOfValves=modification['numOfValves'],
                             capacity=modification['capacity'],
                             ))
        Modification.objects.bulk_create(modifications,
                                         unique_fields=['id'],
                                         ignore_conflicts=True)