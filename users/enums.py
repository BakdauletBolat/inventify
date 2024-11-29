from enum import Enum


class RoleEnum(Enum):
    DIRECTOR = 'Директор'
    DEPARTMENT_DIRECTOR = 'Руководитель отдела'
    DEPARTMENT_HEAD = 'Ведущий cпециалист'
    SALEPERSON = 'Продавец'
    GUEST = 'Гость'
