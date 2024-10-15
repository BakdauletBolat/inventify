from celery import shared_task
from django.core.exceptions import ValidationError

from apps.car.actions.ImportModifcation import ImportModification
from apps.car.models import Modification, Engine
from apps.car.models.Model import ModelCar, ManufacturerType
from apps.car.models.ModificationDraft import ModificationDraft
from apps.product.models.Product import Product
from apps.product.tasks import create_products_draft, create_products
from base.requests import RecarRequest


@shared_task
def import_modification(car_model_id: int):
    ImportModification().run(car_model_id)


@shared_task
def import_modification_recar():
    car_models = ModelCar.objects.values_list('id', flat=True)
    for car_model_id in car_models:
        import_modification.delay(car_model_id)


@shared_task
def import_modification_draft(product_id: int):
    request = RecarRequest()
    modification = request.get_product_modification(product_id)
    ModificationDraft.objects.create(
        product_id=product_id,
        data=modification
    )


@shared_task
def import_model_car(manufacturer_id: int):
    recar_request = RecarRequest()
    cars = []
    car_models = recar_request.get_car_models(manufacturerId=manufacturer_id)
    for model in car_models:
        cars.append(ModelCar(startDate=model.get('startDate', None),
                             endDate=model.get('endDate', None),
                             id=model['id'],
                             name=model['name'],
                             manufacturer_id=manufacturer_id
                             ))
    ModelCar.objects.bulk_create(cars,
                                 unique_fields=['id'],
                                 update_fields=['startDate'],
                                 update_conflicts=True)


@shared_task
def create_modifications_draft():
    products_recar = RecarRequest().get_products()
    product_ids = list(map(lambda x: int(x['id']), products_recar))
    products = ModificationDraft.objects.filter(product_id__in=product_ids)
    difference_products = set(product_ids).difference(products.values_list('product_id', flat=True))
    for product_id in difference_products:
        import_modification_draft.delay(product_id)


@shared_task
def import_car_data_recar():
    create_modifications_draft()
    create_products_draft()
    create_products()


@shared_task
def update_eav_attr(modification_attr: dict, product_id: int):
    modification = modification_attr.get('modification') if modification_attr.get(
        'modification') is not None else {}
    product = Product.objects.get(
        id=product_id,
    )

    product.mileage = modification_attr['mileage']
    try:
        product.eav.bodytype = modification_attr['bodyType']
        product.eav.fueltype = modification_attr['fuelType']
        product.eav.geartype = modification_attr['gearType']
        product.eav.drivetype = modification_attr['driveType']
        product.eav.steeringtype = modification_attr['steeringType']
        product.eav.axleconfiguration = modification_attr['axleConfiguration']
        # product.eav.enginedisplacement = float(modification_attr['engineDisplacement'])

        try:
            product.eav.modelCar = ModelCar.objects.get(id=modification_attr['model']['id'])
        except ModelCar.DoesNotExist as e:
            import_model_car(modification_attr['manufacturer']['id'])
            ImportModification().run(modification_attr['model']['id'])
            product.eav.modelCar = ModelCar.objects.get(id=modification_attr['model']['id'])

        product.eav.power = modification.get('power', None)
        product.eav.capacity = modification.get('capacity', None)
        product.eav.numberofcycle = modification.get('numOfCyl', None)
        product.eav.numberofvalves = modification.get('numOfValves', None)
        product.modification_id = modification.get('id', None)
        product.save()
    except ValidationError as e:
        product.eav.bodytype = modification_attr['bodyType'].replace('C', 'С')
        product.save()
    except Exception as e:
        pass
        # setattr(product.eav, 'engineDisplacement', modification_attr['engineDisplacement'])
        # # product.eav.enginedisplacement = float(modification_attr['engineDisplacement'])
        # product.save()


@shared_task
def create_car_models():
    bulk_create_options = {
        "update_conflicts": True,
        "unique_fields": ['id'],
        "update_fields": ['name']
    }
    recar_request = RecarRequest()
    modification_params = recar_request.get_modification_params()
    manufacturers = []

    for manufacturer in modification_params['manufacturers']['nodes']:
        manufacturers.append(ManufacturerType(id=manufacturer['id'],
                                              name=manufacturer['title']))

    ManufacturerType.objects.bulk_create(manufacturers, **bulk_create_options)

    manufacturers = ManufacturerType.objects.values_list('id', flat=True)
    for manufacturer_id in manufacturers:
        import_model_car.delay(manufacturer_id)


@shared_task
def create_engines():
    modifications = Modification.objects.values_list('id', flat=True)

    for modification_id in modifications:
        create_engine.delay(modification_id)


@shared_task
def create_engine(modification_id):
    recar_request = RecarRequest()
    engines = []
    engines_data = recar_request.get_engines(modification_id)
    for engine in engines_data:
        engines.append(Engine(id=engine['id'],
                              name=engine['name'],
                              modification_id=modification_id))
    Engine.objects.bulk_create(engines,
                               ignore_conflicts=True,
                               unique_fields=['id'],
                               update_fields=['id', 'modification_id'])
