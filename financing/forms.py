from django import forms
from django.contrib.auth import get_user_model
from common.util.querrys import verify_exist, get_client
from accounts.validators import DNIValidator
from .models import Loan, Investment, GuaranteeType, Guarantee


class BaseModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.required:
                field.label = f'*{field.label}'


class GuaranteeTypeCreateForm(BaseModelForm):
    class Meta:
        model = GuaranteeType
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data['name'].lower()
        if verify_exist(GuaranteeType, name=name):
            raise forms.ValidationError(
                'Ya existe este tipo de garantia',
                code='GuaranteeType_exist',
            )
        return name


class GuaranteeCreateForm(BaseModelForm):
    document = forms.CharField(
        label='Cédula del cliente', required=True, validators=[DNIValidator()]
    )

    class Meta:
        model = Guarantee
        fields = ['name', 'type', 'value', 'location', ]

    def clean_document(self):
        client = get_client(self.cleaned_data['document'])
        if client:
            return self.cleaned_data['document']
        raise forms.ValidationError('Cliente no registrado')


class FinancingCreateForm(BaseModelForm):
    """Abstract form for create financing"""

    class Meta:
        exclude = ['application_date', 'approval_date',
                   'checked', 'start_date', 'end_date']
        widgets = {
            'client': forms.HiddenInput(),
            # 'start_date': forms.DateInput(attrs={'type': 'date'}),
            # 'end_date': forms.DateInput(attrs={'type': 'date'}),
            'interest_rate': forms.NumberInput(attrs={'min': 0, 'max': 1})
        }


class LoanCreateForm(FinancingCreateForm):
    """" Formulario para crear un préstamo """
    guarantor = forms.IntegerField(
        label='Fiador', min_value=0, validators=[DNIValidator()], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        client_id = kwargs.get('data', {}).get('client', None)
        if client_id:
            self.fields["guarantee"].queryset = Guarantee.objects.filter(
                client__id=client_id)
        else:
            self.fields["guarantee"].queryset = Guarantee.objects.none()

    def clean_guarantor(self):
        if self.cleaned_data['guarantor'] is None:
            return None
        guarantor = get_client(self.cleaned_data['guarantor'])
        if not guarantor:
            raise forms.ValidationError('El fiador no está registrado')
        client = self.cleaned_data['client']
        if guarantor == client:
            raise forms.ValidationError(
                'El fiador no puede ser la misma persona que solicita el crédito')
        return guarantor.id

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('guarantor', None) is None and cleaned_data.get('guarantee', None) is None:
            self.add_error('guarantor', '')
            self.add_error('guarantee', '')
            self.add_error(
                None, 'Se debe proporcionar una garantía o un fiador')
        return cleaned_data

    class Meta(FinancingCreateForm.Meta):
        model = Loan


class InvestmentCreateForm(FinancingCreateForm):
    """" Formulario para crear una inversión """
    class Meta(FinancingCreateForm.Meta):
        model = Investment


class ApproveFilterForm(forms.Form):
    financing_type = forms.ChoiceField(
        choices=((0, 'loan'), (1, 'investment')))
    financing_state = forms.ChoiceField(
        choices=((0, 'to check'), (1, 'approved'), (2, 'not approved')))
    page = forms.IntegerField(min_value=1)
