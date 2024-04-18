from django.core.validators import RegexValidator
from django.db import models
import re

# RegexValidator for phone number
phone_number_regex = RegexValidator(
    regex=r'^\d{3}-\d{3}-\d{4}$',
    message="Phone number must be entered in the format: '###-###-####'."
)

class PhoneNumberField(models.CharField):
    default_validators = [phone_number_regex]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        value = re.sub(r'[\(\)\-\s+]', '', str(value))
        if len(value) == 10:
            return f"{value[:3]}-{value[3:6]}-{value[6:]}"
        return value