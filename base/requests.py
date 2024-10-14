import requests
from django.core.cache import cache


class Request:
    cache_key = 'access_token'
    cache_timeout = 3500
    url = "https://prod.internal.recar.lt/graphql"

    def get_token_from_cache(self):
        return cache.get(self.cache_key)

    def save_token_to_cache(self, token):
        cache.set(self.cache_key, token, timeout=self.cache_timeout)

    def get_token(self):
        data = {
            "operationName": "ObtainTokens",
            "variables": {
                "payload": {
                    "email": "abdipatahovas@gmail.com",
                    "password": "S123456sev$"
                }
            },
            "query": "mutation ObtainTokens($payload: ObtainTokensInput!) {\n  obtainTokens(payload: $payload) {\n    tokens {\n      ...Tokens\n      __typename\n    }\n    user {\n      id\n      admin\n      email\n      firstname\n      lastname\n      picture {\n        id\n        url\n        __typename\n      }\n      phoneNumber\n      selectedDepartmentId\n      selectedCompanyId\n      selectedVehicleType\n      selectedCartId\n      verified\n      selectedDepartment {\n        id\n        tasksFlowEnabled\n        shipmentsEnabled\n        partsQuantityEnabled\n        rrrEnabled\n        oemPartsEnabled\n        companyId\n        name\n        vehicleType\n        plan {\n          ...Plan\n          __typename\n        }\n        __typename\n      }\n      departments {\n        id\n        tasksFlowEnabled\n        companyId\n        name\n        vehicleType\n        partsQuantityEnabled\n        rrrEnabled\n        oemPartsEnabled\n        shipmentsEnabled\n        __typename\n      }\n      companies {\n        id\n        name\n        __typename\n      }\n      roles {\n        ...Role\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment Role on Role {\n  id\n  name\n  departmentId\n  companyId\n  partnership\n  distributorPermissions {\n    ...Permission\n    __typename\n  }\n  departmentPermissions {\n    ...Permission\n    __typename\n  }\n  companyPermissions {\n    ...Permission\n    __typename\n  }\n  __typename\n}\n\nfragment Permission on Permission {\n  id\n  name\n  __typename\n}\n\nfragment Tokens on Tokens {\n  accessToken\n  refreshToken\n  idToken\n  __typename\n}\n\nfragment Plan on Plan {\n  id\n  name\n  price\n  default\n  __typename\n}\n"
        }

        token = self.get_token_from_cache()
        if token:
            return token

        response = requests.post(
            url=self.url,
            json=data,
        )
        token = response.json()['data']['obtainTokens']['tokens']['accessToken']

        if token:
            self.save_token_to_cache(token)
            return token
        else:
            raise ValueError("Failed to obtain access token")

    def get(self, url, params=None):
        response = requests.get(f'{self.url}{url}',
                                params=params,
                                headers={
                                    'Authorization': 'Bearer ' + self.get_token(),
                                    'Accept': 'application/json'
                                })
        return response.json()

    def post(self, body):
        response = requests.post(self.url, json=body, headers={
            'Authorization': 'Bearer ' + self.get_token(),
            'Accept': 'application/json',
            'Cookie': 'app-locale=ru;'
        }, timeout=120)

        return response.json()


class RecarRequest(Request):

    def get_categories(self):
        data = {
            "operationName": "FetchPartCategories",
            "variables": {
                "size": 10000000
            },
            "query": "query FetchPartCategories($size: Int) { categorySets(size: $size) { nodes { id partCategory { id name __typename } __typename } __typename } }"
        }

        response = self.post(body=data)
        return response['data']['categorySets']['nodes']

    def get_category(self, category_id):
        data = {
            "operationName": "FetchCategorySet",
            "variables": {
                "id": category_id
            },
            "query": "query FetchCategorySet($id: ID) {\n  categorySet(id: $id) {\n    ...CategorySet\n    __typename\n  }\n}\n\nfragment CategorySet on CategorySet {\n  id\n  partCategory {\n    ...PartCategory\n    __typename\n  }\n  nearestParentId\n  children {\n    id\n    nearestParentId\n    partCategory {\n      ...PartCategory\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment PartCategory on PartCategory {\n  id\n  name\n  isPart\n  ebayUkId\n  ebayUsId\n  ebayDeId\n  __typename\n}\n"
        }

        resposne = self.post(body=data)
        return resposne['data']['categorySet']

    def get_modification_params(self):
        data = {
            "operationName": "fetchTpParams",
            "variables": {
                "payload": {
                    "departmentId": "9182",
                    "enabled": True
                },
                "size": 1000
            },
            "query": "query fetchTpParams($payload: GetManufacturersInput, $page: Int, $size: Int) {\n  manufacturers(payload: $payload, page: $page, size: $size) {\n    nodes {\n      title\n      id\n      __typename\n    }\n    __typename\n  }\n  colors {\n    id\n    name\n    __typename\n  }\n  fuelTypes {\n    name\n    id\n    __typename\n  }\n  fuelSystems {\n    id\n    name\n    __typename\n  }\n  coolingTypes {\n    id\n    name\n    __typename\n  }\n  bodyTypes {\n    name\n    id\n    __typename\n  }\n  driveTypes {\n    name\n    id\n    __typename\n  }\n  gearTypes {\n    name\n    id\n    __typename\n  }\n  steeringTypes {\n    name\n    id\n    __typename\n  }\n  suspensionTypes {\n    name\n    id\n    __typename\n  }\n  platformTypes {\n    name\n    id\n    __typename\n  }\n  axleConfigurations {\n    name\n    id\n    __typename\n  }\n}\n"
        }

        response = self.post(data)
        return response['data']

    def get_car_models(self, manufacturerId: int):
        data = {
            "operationName": "fetchModels",
            "variables": {
                "payload": {
                    "manufacturerId": manufacturerId,
                    "departmentId": "9182",
                    "enabled": True
                },
                "size": 1000
            },
            "query": "query fetchModels($payload: GetModelsInput, $page: Int, $size: Int) {\n  models(payload: $payload, page: $page, size: $size) {\n    nodes {\n      name: title\n      id\n      endDate\n      startDate\n      __typename\n    }\n    __typename\n  }\n}\n"
        }
        response = self.post(data)
        return response['data']['models']['nodes']

    def get_modifications(self, modelId: int):
        data = {
            "operationName": "fetchModifications",
            "variables": {
                "payload": {
                    "modelId": modelId,
                    "departmentId": "9182",
                    "enabled": True
                },
                "size": 1000
            },
            "query": "query fetchModifications($payload: GetModificationsInput, $page: Int, $size: Int) {\n  modifications(payload: $payload, page: $page, size: $size) {\n    nodes {\n      ...Modification\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment Modification on Modification {\n  id\n  name: title\n  fullTitle\n  type\n  modelId\n  startDate\n  endDate\n  bodyType\n  driveType\n  fuelType\n  gearType\n  power\n  numOfCyl\n  numOfValves\n  capacity\n  platformType\n  axleConfiguration\n  suspensionTypes {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n"
        }
        response = self.post(data)
        return response['data']['modifications']['nodes']

    def get_engines(self, modificationId: int):
        data = {
            "operationName": "getEngines",
            "variables": {
                "payload": {
                    "modificationId": modificationId
                },
                "size": 1000
            },
            "query": "query getEngines($payload: GetEnginesInput) {\n  engines(payload: $payload) {\n    nodes {\n      id\n      name: title\n      __typename\n    }\n    __typename\n  }\n}\n"
        }
        response = self.post(data)
        return response['data']['engines']['nodes']

    def get_products(self, statuses=None):
        if statuses is None:
            statuses = ["not_parsed", "in_stock", "reserved", "sold"]
        data = {
            "operationName": "FetchParts",
            "variables": {
                "payload": {
                    "statuses": statuses,
                    "defaultQuery": False,
                    "departmentIds": "9182",
                    "partnership": False,
                    "isRootsChild": True,
                    "nearestParentId": None
                },
                "page": "1",
                "size": "100000"
            },
            "query": "query FetchParts($payload: GetPartsInput, $size: Int, $page: Int) {\n  parts(payload: $payload, size: $size, page: $page) {\n    nodes {\n      id\n                                         __typename\n    }\n    __typename\n  }\n}\n"
        }
        response = self.post(data)
        return response['data']['parts']['nodes']

    def get_product(self, product_id: int):
        data = {
            "operationName": "FetchPart",
            "variables": {
                "id": product_id
            },
            "query": "query FetchPart($id: ID) {\n  part(id: $id) {\n    ...Part\n    __typename\n  }\n}\n\nfragment Part on Part {\n  id\n  createdAt\n  updatedAt\n  price\n  defective\n  status\n  comment\n  qrComment\n  colorCode\n  defectComment\n  deleteComment\n  sellPrice\n  suggestedPrice {\n    previousYear\n    previousMonth\n    previousPrice\n    currentYear\n    currentMonth\n    currentPrice\n    percentage\n    __typename\n  }\n  deleted\n  orderId\n  height\n  width\n  length\n  weight\n  groupedSaleId\n  nearestParentId\n  dalysltPart {\n    price\n    link\n    enabled\n    __typename\n  }\n  tasks {\n    id\n    type\n    assignedUser {\n      id\n      firstname\n      lastname\n      __typename\n    }\n    completeDate\n    status\n    parentTaskId\n    __typename\n  }\n  children {\n    id\n    nearestParentId\n    price\n    status\n    quantity\n    originalPartId\n    inputNearestParent {\n      id\n      __typename\n    }\n    tasks {\n      id\n      name\n      type\n      assignedUser {\n        id\n        firstname\n        lastname\n        __typename\n      }\n      completeDate\n      status\n      parentTaskId\n      __typename\n    }\n    category {\n      id\n      name\n      isPart\n      __typename\n    }\n    __typename\n  }\n  department {\n    id\n    name\n    vehicleType\n    partsQuantityEnabled\n    tasksFlowEnabled\n    __typename\n  }\n  oemCodes {\n    id\n    code\n    __typename\n  }\n  category {\n    ...PartCategory\n    __typename\n  }\n  location {\n    id\n    name\n    __typename\n  }\n  suggestedLocation {\n    id\n    name\n    __typename\n  }\n  inputParent {\n    id\n    isGroupedSale\n    comment\n    oemCodes {\n      id\n      code\n      __typename\n    }\n    location {\n      id\n      name\n      __typename\n    }\n    category {\n      id\n      name\n      __typename\n    }\n    picturesV2 {\n      id\n      order\n      s105x70\n      s195x130\n      s360x240\n      s570x380\n      s1050x700\n      optimized\n      __typename\n    }\n    __typename\n  }\n  inputNearestParent {\n    id\n    isGroupedSale\n    comment\n    category {\n      ...PartCategory\n      __typename\n    }\n    location {\n      id\n      name\n      __typename\n    }\n    oemCodes {\n      id\n      code\n      __typename\n    }\n    picturesV2 {\n      id\n      order\n      s105x70\n      s195x130\n      s360x240\n      s570x380\n      s1050x700\n      optimized\n      __typename\n    }\n    __typename\n  }\n  inputUser {\n    id\n    picture {\n      id\n      url\n      __typename\n    }\n    firstname\n    lastname\n    __typename\n  }\n  amazonEnabled\n  quantity\n  originalPartId\n  visible\n  isWheel\n  vehicleType\n  __typename\n}\n\nfragment PartCategory on PartCategory {\n  id\n  name\n  isPart\n  ebayUkId\n  ebayUsId\n  ebayDeId\n  __typename\n}\n"
        }

        response = self.post(data)
        return response['data']['part']

    def get_product_modification(self, product_id: int):
        data = {
            "operationName": "FetchPartTpParameters",
            "variables": {
                "id": product_id
            },
            "query": "query FetchPartTpParameters($id: ID) {\n  part(id: $id) {\n    id\n    ...TpParameters\n    __typename\n  }\n}\n\nfragment TpParameters on Part {\n  vehicleSpecifications {\n    id\n    model {\n      ...Model\n      __typename\n    }\n    manufacturer {\n      ...Manufacturer\n      __typename\n    }\n    modification {\n      ...Modification\n      __typename\n    }\n    engine {\n      id\n      name: title\n      __typename\n    }\n    vinCode\n    color\n    bodyType\n    driveType\n    gearType\n    steeringType\n    fuelType\n    fuelSystem\n    coolingType\n    engineDisplacement\n    year\n    mileage\n    mileageType\n    platformType\n    axleConfiguration\n    frontSuspensionType\n    rearSuspensionType\n    __typename\n  }\n  __typename\n}\n\nfragment Model on Model {\n  id\n  name: title\n  startDate\n  endDate\n  __typename\n}\n\nfragment Manufacturer on Manufacturer {\n  name: title\n  id\n  __typename\n}\n\nfragment Modification on Modification {\n  id\n  name: title\n  fullTitle\n  type\n  modelId\n  startDate\n  endDate\n  bodyType\n  driveType\n  fuelType\n  gearType\n  power\n  numOfCyl\n  numOfValves\n  capacity\n  platformType\n  axleConfiguration\n  suspensionTypes {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n"
        }
        response = self.post(data)
        return response['data']['part']['vehicleSpecifications']

    def get_warehouses(self, page, size):
        data = {
            "operationName": "fetchLocations",
            "variables": {
                "payload": {
                    "departmentIds": "9182"
                },
                "page": page,
                "size": size,
                "sort": {
                    "column": "parts_count",
                    "order": "asc"
                },
                "showId": False,
                "showName": True,
                "showDepartment": False,
                "showType": False,
                "showPartCategories": True,
                "showPartsCount": True,
                "showReservedPartsCount": True,
                "showGroupedSalesCount": False,
                "showBarcode": False
            },
            "query": "query fetchLocations($payload: GetLocationsInput, $size: Int, $page: Int, $showDepartment: Boolean!, $showName: Boolean!, $showType: Boolean!, $showPartCategories: Boolean!, $showPartsCount: Boolean!, $showReservedPartsCount: Boolean!, $showGroupedSalesCount: Boolean!) {\n  locations(payload: $payload, size: $size, page: $page) {\n    nodes {\n      id\n      groupedSalesCount @include(if: $showGroupedSalesCount)\n      name @include(if: $showName)\n      department @include(if: $showDepartment) {\n        id\n        name\n        __typename\n      }\n      partCategories @include(if: $showPartCategories) {\n        id\n        name\n        __typename\n      }\n      partsCount @include(if: $showPartsCount)\n      reservedPartsCount @include(if: $showReservedPartsCount)\n      partsSpace @include(if: $showPartsCount)\n      type @include(if: $showType)\n      __typename\n    }\n    __typename\n  }\n}\n"
        }
        response = self.post(data)
        return response['data']['locations']['nodes']

    def get_warehouse_detail(self, locationId):
        data = {
            "operationName": "FetchLocationParts",
            "variables": {
                "payload": {
                    "nearestParentId": None,
                    "locationId": locationId
                },
                "page": 1,
                "size": "300"
            },
            "query": "query FetchLocationParts($payload: GetPartsInput, $page: Int, $size: Int) {\n  parts(payload: $payload, page: $page, size: $size) {\n    nodes {\n      id\n            location {\n        id\n        name\n        departmentId\n        __typename\n      }\n      oemCodes {\n        id\n        code\n        __typename\n      }\n            quantity\n      __typename\n    }\n    __typename\n  }\n}\n"
        }
        response = self.post(data)
        return response['data']['parts']['nodes']