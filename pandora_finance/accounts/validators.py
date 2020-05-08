  
import re
from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible

@deconstructible
class DNIValidator(RegexValidator):
    regex = r'^[0-9]{6,10}$'
    message = 'Ingresa una cedula valida. Este valor solo puede contener numeros.'
    code='invalid_document'


@deconstructible
class PhoneValidator(RegexValidator):
    regex = r'^[0-9]{10}$'
    message = "El número de teléfono debe ingresarse en el formato: '1111111111'. Y debe tener 10 digitos"
    code='invalid_phone'


@deconstructible
class NameValidator(RegexValidator):
    regex = r'^[^0-9_!¡?÷?¿/\\+=@#$%ˆ&*(){}|~<>;:[\]]{2,}$'
    message = "Nombre no valido"
    code='invalid_name'
