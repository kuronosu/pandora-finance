from django.template.defaulttags import register
from financing.models import Payment

@register.filter
def get_verbose_payment_method(value):
    for PAYMENT_METHOD in Payment.PAYMENT_METHODS_CHOICES:
        if PAYMENT_METHOD[0] == value:
            return PAYMENT_METHOD[1]
    return ''