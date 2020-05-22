  
import re
from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible

@deconstructible
class BankAccountValidator(RegexValidator):
    regex = r'^[0-9]+$'
    message = "La cuenta bancaria solo es numerica"
    code='invalid_bank_account'
