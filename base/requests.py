import requests


class Request:
    data = {
        "operationName": "ObtainTokens",
        "variables": {
            "payload": {
                "email": "abdipatahovas@gmail.com",
                "password": "S123456sev$"
            }
        },
        "query": """mutation ObtainTokens($payload: ObtainTokensInput!) {
  obtainTokens(payload: $payload) {
    tokens {
      ...Tokens
      __typename
    }
    user {
      id
      admin
      email
      firstname
      lastname
      picture {
        id
        url
        __typename
      }
      phoneNumber
      selectedDepartmentId
      selectedCompanyId
      selectedVehicleType
      verified
      selectedDepartment {
        id
        tasksFlowEnabled
        shipmentsEnabled
        partsQuantityEnabled
        rrrEnabled
        companyId
        name
        vehicleType
        plan {
          ...Plan
          __typename
        }
        __typename
      }
      departments {
        id
        tasksFlowEnabled
        companyId
        name
        vehicleType
        partsQuantityEnabled
        rrrEnabled
        shipmentsEnabled
        __typename
      }
      companies {
        id
        name
        __typename
      }
      roles {
        ...Role
        __typename
      }
      __typename
    }
    __typename
  }
}

fragment Role on Role {
  id
  name
  departmentId
  companyId
  partnership
  visible
  distributorPermissions {
    ...Permission
    __typename
  }
  departmentPermissions {
    ...Permission
    __typename
  }
  companyPermissions {
    ...Permission
    __typename
  }
  __typename
}

fragment Permission on Permission {
  id
  name
  __typename
}

fragment Tokens on Tokens {
  accessToken
  refreshToken
  idToken
  __typename
}

fragment Plan on Plan {
  id
  name
  price
  default
  __typename
}
"""
    }

    url = "https://prod.internal.recar.lt/graphql"

    def get_token(self):
        response = requests.post(
            url=self.url,
            json=self.data,
        )
        return response.json()['data']['obtainTokens']['tokens']['accessToken']

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
        })

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
