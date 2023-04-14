from django.core import validators
from django.db import models

REGEX_KZ = r'^\+7(?:[ \-])?(\d{3})(?:[ \-])?(\d{3})(?:[ \-])?(\d{2})(?:[ \-])?(\d{2})$'


class PhoneField(models.CharField):
    phone_regex = validators.RegexValidator(
        regex=REGEX_KZ,
        message="Телефонный номер должен быть в формате: '+77777777777'. Допустимо от 10 до 20 цифр."
    )
    default_validators = [phone_regex]

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 20)
        super(PhoneField, self).__init__(*args, **kwargs)
