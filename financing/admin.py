from django.contrib import admin
from .models import Investment, Loan, Guarantee, GuaranteeType, LoanPayment, InvestmentPayment

# Register your models here.


@admin.register(Investment, Loan)
class FinanceAdmin(admin.ModelAdmin):
    ordering = ('application_date', 'code',)
    list_display = ('code', 'client', 'approval_date', 'application_date')


@admin.register(Guarantee, GuaranteeType)
class GuaranteeAdmin(admin.ModelAdmin):
    pass

@admin.register(LoanPayment, InvestmentPayment)
class PaymentAdmin(admin.ModelAdmin):
    pass
