from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.core.validators import MinValueValidator
from django.core.exceptions import ImproperlyConfigured
from common.util import generate_code
from .validators import BankAccountValidator, VoucherValidator


def generate_code_guarantee():
    return generate_code('Guarantee')


def generate_code_loan():
    return generate_code('Loan')


def generate_code_investment():
    return generate_code('Investment')


class GuaranteeType(models.Model):
    name = models.CharField(
        max_length=50, verbose_name='Tipo de garantía', unique=True)

    def __str__(self):
        return self.name


class Guarantee(models.Model):
    code = models.UUIDField('Código', primary_key=True,
                            default=generate_code_guarantee, editable=False)
    name = models.CharField(
        max_length=50, verbose_name='Nombre de la garantía')
    type = models.ForeignKey(
        GuaranteeType, on_delete=models.CASCADE, verbose_name='Tipo')
    value = models.DecimalField('Valor', decimal_places=2, max_digits=12, validators=[
                                MinValueValidator(Decimal('1.0'))])
    location = models.CharField('Ubicación', max_length=100)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Cliente', related_name='guarantee_owner', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Finance(models.Model):
    name = models.CharField('Nombre', max_length=15, blank=True, null=True)
    application_date = models.DateTimeField(
        'Fecha de solicitud', default=timezone.now)
    approval_date = models.DateTimeField(
        'Fecha de aprobación', blank=True, null=True)
    start_date = models.DateField('Fecha de inicio', blank=True, null=True)
    end_date = models.DateField('Fecha de término', blank=True, null=True)
    amount = models.DecimalField('Monto', decimal_places=2, max_digits=12, validators=[
                                 MinValueValidator(Decimal('1.0'))])
    interest_rate = models.DecimalField('Tasa de interés', decimal_places=2, max_digits=5, validators=[
        MinValueValidator(Decimal('0'))])
    checked = models.BooleanField('Revisado', default=False)
    installments_number = models.PositiveSmallIntegerField(
        'Número de cuotas', validators=[MinValueValidator(1)])

    @classmethod
    def get_approved(cls):
        return (cls.objects
                .exclude(approval_date=None)
                .filter(checked=True)
                .order_by('application_date'))

    @classmethod
    def get_not_approved(cls):
        return (cls.objects
                .filter(approval_date=None, checked=True)
                .order_by('application_date'))

    @classmethod
    def get_to_check(cls):
        return (cls.objects
                .filter(approval_date=None, checked=False)
                .order_by('application_date'))

    @classmethod
    def get_actives(cls, payment_cls):
        active_finance = [finance.code for finance in cls.get_approved()
                          if payment_cls.to_pay(finance) != 0]
        return cls.objects.filter(code__in=active_finance)

    @classmethod
    def group_by_month(cls, attr):
        if attr not in ['application_date', 'approval_date', 'start_date', 'end_date']:
            raise ImproperlyConfigured(
                'The attr must be one of application_date, approval_date, start_date, end_date')
        return [{'month': d['month'].strftime('%Y-%m'), 'count': d['c']} for d in
                cls.objects.exclude(**{attr: None}).annotate(month=TruncMonth(attr)).values('month').annotate(c=Count('code')).values('month', 'c')]

    def is_active(self):
        if hasattr(self, 'payment_related_name'):
            return getattr(self, self.payment_related_name).filter(effective_date=None).count() != 0

    class Meta:
        abstract = True


class Loan(Finance):
    payment_related_name = 'loan_payment'
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
    payment_related_name = 'investment_payment'
    code = models.UUIDField('Código', primary_key=True,
                            default=generate_code_investment, editable=False)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Cliente', related_name='investment_client', on_delete=models.CASCADE)
    bank_account = models.CharField(
        'Numero de cuenta', max_length=30, validators=[BankAccountValidator()])

    class Meta:
        verbose_name = 'Inversión'
        verbose_name_plural = 'Inversiónes'


class Payment(models.Model):
    PAYMENT_METHODS_CHOICES = (
        (0, 'Pago en efectivo'),
        (1, 'Depósito bancario'),
        (2, 'Cheque'),
        (3, 'Transferencia directa'),
    )
    amount = models.DecimalField('Monto', decimal_places=2, max_digits=12)
    planned_date = models.DateField('Fecha planificada')
    effective_date = models.DateTimeField(
        'Fecha efectiva', blank=True, null=True)
    method = models.PositiveSmallIntegerField(
        'Método de pago', choices=PAYMENT_METHODS_CHOICES, blank=True, null=True)
    voucher = models.CharField('Comprobante', max_length=100, validators=[
                               VoucherValidator()], blank=True, null=True)

    class Meta:
        abstract = True

    @classmethod
    def to_pay(cls, f):
        return cls.objects.filter(finance=f, effective_date=None).count()


class LoanPayment(Payment):
    finance = models.ForeignKey(Loan, verbose_name='Préstamo',
                                related_name='loan_payment', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Pago de préstamo'
        verbose_name_plural = 'Pagos de préstamo'


class InvestmentPayment(Payment):
    finance = models.ForeignKey(Investment, verbose_name='Inversión',
                                related_name='investment_payment', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Pago de inversión'
        verbose_name_plural = 'Pagos de inversión'
