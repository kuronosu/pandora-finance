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
from .validators import DNIValidator

UserModel = get_user_model()


class SearchClientForm(forms.Form):
    document = forms.CharField(
        label='Cedula del cliente', required=True, validators=[DNIValidator()])
    widgets = {'document': forms.NumberInput(attrs={'min': 0})}


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
            field.label += ':'

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
