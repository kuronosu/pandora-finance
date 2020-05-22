from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
from common.util import generate_code
from .validators import BankAccountValidator


def generate_code_guarantee():
    return generate_code('Guarantee')


def generate_code_loan():
    return generate_code('Loan')


def generate_code_investment():
    return generate_code('Investment')


class GuaranteeType(models.Model):
    name = models.CharField(max_length=50, verbose_name='Tipo de garantía')

    def __str__(self):
        return self.name


class Guarantee(models.Model):
    code = models.UUIDField('Código', primary_key=True,
                            default=generate_code_guarantee, editable=False)
    type = models.ForeignKey(
        GuaranteeType, on_delete=models.CASCADE, verbose_name='Tipo')
    value = models.DecimalField('Valor', decimal_places=2, max_digits=12, validators=[
                                MinValueValidator(Decimal('1.0'))])
    location = models.CharField('Ubicación', max_length=100)


class Finance(models.Model):
    application_date = models.DateTimeField(
        'Fecha de solicitud', default=timezone.now)
    approval_date = models.DateTimeField(
        'Fecha de aprobación', blank=True, null=True)
    start_date = models.DateField('Fecha de inicio')
    end_date = models.DateField('Fecha de término')
    amount = models.DecimalField('Monto', decimal_places=2, max_digits=12, validators=[
                                 MinValueValidator(Decimal('1.0'))])
    interest_rate = models.DecimalField('Tasa de interés', decimal_places=2, max_digits=5, validators=[
        MinValueValidator(Decimal('0'))])

    class Meta:
        abstract = True


class Loan(Finance):
    code = models.UUIDField('Código', primary_key=True,
                            default=generate_code_loan, editable=False)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Cliente', related_name='loan_client', on_delete=models.CASCADE)
    guarantor = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Fiador', related_name='loan_guarantor', on_delete=models.CASCADE, blank=True, null=True)
    guarantee = models.ForeignKey(
        Guarantee, verbose_name='Garantia', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        # constraints = [
        #     CheckConstraint(check=(Q(guarantor__is_null=True) & Q(guarantee__is_null=False)) | (
        #         Q(guarantor__is_null=False) & Q(guarantee__is_null=True)), name='guarantor_guarantee_required'),
        # ]
        verbose_name = 'Préstamo'
        verbose_name_plural = 'Préstamos'


class Investment(Finance):
    code = models.UUIDField('Código', primary_key=True,
                            default=generate_code_investment, editable=False)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Cliente', related_name='investment_client', on_delete=models.CASCADE)
    bank_account = models.CharField(
        'Numero de cuenta', max_length=30, validators=[BankAccountValidator()])

    class Meta:
        verbose_name = 'Inversión'
        verbose_name_plural = 'Inversiónes'
