from django import forms
from django.contrib.auth import get_user_model
from accounts.validators import DNIValidator
from common.util.querrys import get_client
from .models import Loan, Investment


class FinanceCreateForm(forms.ModelForm):
    """Abstract form for create financing"""
    document = forms.CharField(
        label='Cedula del cliente', required=True, validators=[DNIValidator()])

    def __init__(self, *args, **kwargs):
        super(FinanceCreateForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.required:
                field.label = f'*{field.label}'
            field.label += ':'

    def clean_document(self):
        if not get_client(self.cleaned_data['document']):
            raise forms.ValidationError(
                'Cédula no registrada',
                code='document_not_exist',
            )
        return self.cleaned_data['document']

    class Meta:
        exclude = ['client', 'application_date', 'approval_date']
        widgets = {
            'document': forms.NumberInput(attrs={'min': 0}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'interest_rate': forms.NumberInput(attrs={'min': 0, 'max': 1})
        }


class LoanCreateForm(FinanceCreateForm):
    """" Formulario para crear un préstamo """
    class Meta(FinanceCreateForm.Meta):
        model = Loan


class InvestmentCreateForm(FinanceCreateForm):
    """" Formulario para crear una inversión """
    class Meta(FinanceCreateForm.Meta):
        model = Investment
