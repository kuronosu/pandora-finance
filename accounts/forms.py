import re

from django import forms
from django.utils.text import capfirst
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import (
    PasswordChangeForm, PasswordResetForm, SetPasswordForm, UserCreationForm
)
from common.util.querrys import get_client
from .validators import DNIValidator, NameValidator

UserModel = get_user_model()


class SearchClientDocumentForm(forms.Form):
    document = forms.CharField(
        label='Cedula del cliente', required=True, validators=[DNIValidator()])
    widgets = {'document': forms.NumberInput(attrs={'min': 0})}


class SearchClientNameForm(forms.Form):
    name = forms.CharField(label='Nombre del cliente:',
                           required=False, validators=[NameValidator()],
                           widget=forms.TextInput(attrs={'placeholder': 'Nombre del cliente'}))
    document = forms.CharField(
        label='Cedula del cliente', required=False, validators=[DNIValidator()],
        widget=forms.NumberInput(attrs={'min': 0, 'placeholder': 'Cedula del cliente'}))


class AuthenticationForm(AuthenticationForm):
    icons = {
        'username': 'user',
        'password': 'unlock'
    }


class SignUpForm(UserCreationForm):

    error_messages = {**UserCreationForm.error_messages, **{
        'client_exist': 'Cédula ya registrada',
    }}

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        # self.fields['document'].attr
        for field in self.fields.values():
            if field.required:
                field.label = f'*{field.label}'

    def clean_document(self):
        if get_client(self.cleaned_data['document']):
            raise forms.ValidationError(
                self.error_messages['client_exist'],
                code='client_exist',
            )
        return self.cleaned_data['document']

    class Meta(UserCreationForm.Meta):
        model = UserModel
        fields = [
            'document',
            'first_name',
            'last_name',
            'phone_number',
            'email',
            'address1',
            'address2',
            'birthdate',
        ]
        widgets = {
            'document': forms.NumberInput(attrs={'min': 0}),
            'birthdate': forms.DateInput(attrs={'type': 'date'}),
            # 'phone_number': forms.NumberInput(attrs={'value': '+57'})
        }
