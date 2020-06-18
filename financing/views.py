from datetime import datetime
from django.conf import settings
from django.utils import timezone
from django.urls import reverse_lazy
from django.http.response import JsonResponse
from django.contrib.auth import get_user_model
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from common.mixins import SetClientMixin, AddToContextMixin
from accounts.mixins import LoginEmployeeRequiredMixin, CanApproveMixin
from accounts.forms import SearchClientDocumentForm

from .models import Loan, Investment, Guarantee, GuaranteeType
from .forms import (LoanCreateForm, InvestmentCreateForm,
                    GuaranteeTypeCreateForm, GuaranteeCreateForm)


class CreateGuaranteeTypeView(LoginEmployeeRequiredMixin, AddToContextMixin, CreateView):
    model = GuaranteeType
    login_url = reverse_lazy('accounts:login')
    template_name = 'general_form.html'
    form_class = GuaranteeTypeCreateForm
    success_url = reverse_lazy('financing:create_guarantee')
    add_to_context = {
        'title': 'Registrar tipo de garantia',
        'page_title': 'Tipo de Garantia',
        'submit_text': 'Guardar',
    }


class CreateGuaranteeView(LoginEmployeeRequiredMixin, SetClientMixin, AddToContextMixin, CreateView):
    model = Guarantee
    login_url = reverse_lazy('accounts:login')
    template_name = 'general_form.html'
    form_class = GuaranteeCreateForm
    success_url = reverse_lazy('financing:create_loan')
    add_to_context = {
        'page_title': 'Garantia',
        'submit_text': 'Guardar',
        'title': 'Crear Garantia',
    }


class CreateLoanView(LoginEmployeeRequiredMixin, AddToContextMixin, CreateView):
    model = Loan
    login_url = reverse_lazy('accounts:login')
    template_name = 'financing/create.html'
    form_class = LoanCreateForm
    success_url = '/'  # reverse_lazy('')
    add_to_context = {
        'submit_text': 'Guardar',
        'title': 'Crear préstamo',
        'page_title': 'Crear préstamo',
        'search_client_form': SearchClientDocumentForm,
    }


class CreateInvestmentView(LoginEmployeeRequiredMixin, AddToContextMixin, CreateView):
    model = Investment
    login_url = reverse_lazy('accounts:login')
    template_name = 'financing/create.html'
    form_class = InvestmentCreateForm
    success_url = '/'  # reverse_lazy('')
    add_to_context = {
        'submit_text': 'Guardar',
        'title': 'Crear inversión',
        'page_title': 'Crear inversión',
        'search_client_form': SearchClientDocumentForm,
    }


class FinancingApproveListView(CanApproveMixin, AddToContextMixin, TemplateView):
    template_name = 'financing/approve.html'
    errors = []
    add_to_context = {
        'page_title': 'Aprobar',
    }

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        print(request.POST, kwargs)
        model = request.POST.get('model', None)
        approve = request.POST.get('approve', None)
        financing = request.POST.get('financing', None)
        if model == 'financing.investment':
            model = Investment
        elif model == 'financing.loan':
            model = Loan
        else:
            model = None

        if approve == '1':
            approve = True
        elif approve == '0':
            approve = False
        else:
            approve = None

        if approve is None or model is None:
            self.errors = ['Error al realizar lo operacion']
            return super().get(request, *args, **kwargs)
        try:
            obj = model.objects.get(code=financing)
            if obj.checked == False:
                if approve == True:
                    tz = timezone.now()
                    obj.approval_date = tz
                    obj.start_date = datetime(tz.year, tz.month + 1, 1)
                    new_month = obj.installments_number + 1
                    new_year = tz.year
                    if (new_month > 12):
                        new_year += new_month // 12
                        new_month = new_month % 12 + tz.month
                    obj.end_date = datetime(new_year, new_month, 1)
                else:
                    obj.approval_date = None
                    obj.start_date = None
                    obj.end_date = None
                obj.checked = True
                obj.save()
            else:
                self.errors = [
                    'Error al realizar lo operacion, esta financiacion ya fue revisada']
        except:
            self.errors = ['Error al realizar lo operacion']
        print(self.errors)
        return super().get(request, *args, **kwargs)

    def dynamic_context(self):
        return {
            'errors': self.errors
        }
