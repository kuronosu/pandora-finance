# Generated by Django 3.0.6 on 2020-06-21 21:55

from django.db import migrations, models
import financing.validators


class Migration(migrations.Migration):

    dependencies = [
        ('financing', '0004_investmentpayment_loanpayment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investmentpayment',
            name='method',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(0, 'Pago en efectivo'), (1, 'Depósito bancario'), (2, 'Cheque'), (3, 'Transferencia directa')], null=True, verbose_name='Método de pago'),
        ),
        migrations.AlterField(
            model_name='investmentpayment',
            name='voucher',
            field=models.CharField(blank=True, max_length=100, null=True, validators=[financing.validators.VoucherValidator()], verbose_name='Comprobante'),
        ),
        migrations.AlterField(
            model_name='loanpayment',
            name='method',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(0, 'Pago en efectivo'), (1, 'Depósito bancario'), (2, 'Cheque'), (3, 'Transferencia directa')], null=True, verbose_name='Método de pago'),
        ),
        migrations.AlterField(
            model_name='loanpayment',
            name='voucher',
            field=models.CharField(blank=True, max_length=100, null=True, validators=[financing.validators.VoucherValidator()], verbose_name='Comprobante'),
        ),
    ]
