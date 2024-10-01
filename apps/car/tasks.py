from celery import shared_task

from apps.car.models.Model import ModelCar
from apps.car.models.ModificationDraft import ModificationDraft
from apps.product.models.Product import Product
from apps.product.tasks import create_products_draft, create_products
from base.requests import RecarRequest


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
    # create_modifications_draft()
    # create_products_draft()
    create_products()



def update_eav_attr(modification_attr: ModificationDraft):
    modification = modification_attr.data.get('modification') if modification_attr.data.get(
        'modification') is not None else {}
    product = Product.objects.get(
        id=modification_attr.product_id,
    )

    product.mileage = modification_attr.data['mileage']
    try:
        product.eav.bodytype = modification_attr.data['bodyType']
        product.eav.fueltype = modification_attr.data['fuelType']
        product.eav.geartype = modification_attr.data['gearType']
        product.eav.drivetype = modification_attr.data['driveType']
        product.eav.steeringtype = modification_attr.data['steeringType']
        product.eav.axleconfiguration = modification_attr.data['axleConfiguration']
        try:
            product.eav.modelCar = ModelCar.objects.get(id=modification_attr.data['model']['id'])
        except Exception as e:
            print(modification_attr.id)
        product.eav.power = modification.get('power', None)
        product.eav.capacity = modification.get('capacity', None)
        product.eav.numberofcycle = modification.get('numOfCyl', None)
        product.eav.numberofvalves = modification.get('numOfValves', None)
        product.eav.enginedisplacement = modification.get('engineDisplacement', None)
        product.modification_id = modification.get('id', None)
        product.save()
    except Exception as e:
        product.eav.bodytype = modification_attr.data['bodyType'].replace('C', 'С')
        product.save()
