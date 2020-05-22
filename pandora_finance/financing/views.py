from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.views.generic.edit import CreateView
from common.mixins import SetClientMixin, GeneralFormContexMixin
from accounts.mixins import LoginEmployeeRequiredMixin


from .models import Loan, Investment
from .forms import LoanCreateForm, InvestmentCreateForm


class CreateLoan(LoginEmployeeRequiredMixin, GeneralFormContexMixin, SetClientMixin, CreateView):
    model = Loan
    login_url = reverse_lazy('accounts:login')
    template_name = 'general_form.html'  # 'financing/loan_create.html'
    form_class = LoanCreateForm
    success_url = '/'  # reverse_lazy('')
    title = 'Crear préstamo'
    page_title = 'Crear préstamo'
    submit_text = 'Guardar'


class CreateInvestment(LoginEmployeeRequiredMixin, GeneralFormContexMixin, SetClientMixin, CreateView):
    model = Investment
    login_url = reverse_lazy('accounts:login')
    template_name = 'general_form.html'  # 'financing/investment_create.html'
    form_class = InvestmentCreateForm
    success_url = '/'  # reverse_lazy('')
    title = 'Crear inversión'
    page_title = 'Crear inversión'
    submit_text = 'Guardar'
