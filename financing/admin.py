from django.contrib import admin
from .models import Investment, Loan

# Register your models here.


@admin.register(Investment, Loan)
class FinanceAdmin(admin.ModelAdmin):
    model = Investment
    ordering = ('code',)
    list_display = ('code', 'client', 'approval_date')
