  
import re
from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible

@deconstructible
class BankAccountValidator(RegexValidator):
    regex = r'^[0-9]+$'
    message = "La cuenta bancaria solo es numerica"
    code='invalid_bank_account'

@deconstructible
class VoucherValidator(RegexValidator):
    regex = r'^[0-9]+$'
    message = "El comprobante solo debe tener numeros"
    code='invalid_voucher'
