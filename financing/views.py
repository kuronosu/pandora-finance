import json
from datetime import datetime
from django.utils import timezone
from django.conf import settings
from django.utils import timezone
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView
from django.db.models.query import EmptyQuerySet
from django.db.models import (Sum, Avg, Count, Variance, Max, Q,
                              Min, Value, BooleanField, Case, When)
from common.mixins import SetClientMixin, AddToContextMixin
from accounts.forms import SearchClientDocumentForm
from accounts.mixins import (LoginEmployeeRequiredMixin, AccessMixin,
                             ChiefCreditLoginRequiredMixin,)
from .models import (Loan, Investment, Guarantee, GuaranteeType,
                     LoanPayment, InvestmentPayment)
from .forms import (LoanCreateForm, InvestmentCreateForm, SearchFinancingForm,
                    GuaranteeTypeCreateForm, GuaranteeCreateForm)


def generate_payment_schedule(finance_object):
    if type(finance_object) == Loan:
        Payment = LoanPayment
    elif type(finance_object) == Investment:
        Payment = InvestmentPayment
    else:
        return

    # A = Vp*((i*(1+i)^n)/(1+i)^n - 1)
    _ = pow(1 + finance_object.interest_rate,
            finance_object.installments_number)
    amount = finance_object.amount * \
        ((finance_object.interest_rate * _) / (_ - 1))

    for i in range(finance_object.installments_number):
        try:
            year = finance_object.start_date.year
            month = finance_object.start_date.month + i
            day = finance_object.start_date.day if finance_object.start_date.day <= 28 else 28
            if month > 12:
                year += month // 12
                month %= 12
            planned_date = datetime(year, month, day)
            Payment.objects.create(
                finance=finance_object, amount=amount, planned_date=planned_date)
        except Exception as e:
            pass


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


class FinancingApproveListView(ChiefCreditLoginRequiredMixin, AddToContextMixin, TemplateView):
    template_name = 'financing/approve.html'
    errors = []
    add_to_context = {
        'page_title': 'Aprobar',
    }

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
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
                    obj.start_date = datetime(tz.year, tz.month + 1, 10)
                    new_month = tz.month + obj.installments_number
                    new_year = tz.year
                    if (new_month > 12):
                        new_year += new_month // 12
                        new_month = new_month % 12
                    obj.end_date = datetime(new_year, new_month, 10)
                else:
                    obj.approval_date = None
                    obj.start_date = None
                    obj.end_date = None
                obj.checked = True
                obj.save()
                if obj.approval_date:
                    generate_payment_schedule(obj)
            else:
                self.errors = [
                    'Error al realizar lo operacion, esta financiacion ya fue revisada']
        except Exception as e:
            self.errors = ['Error al realizar lo operacion']
        return super().get(request, *args, **kwargs)

    def dynamic_context(self):
        return {
            'errors': self.errors
        }


class StatisticsView(ChiefCreditLoginRequiredMixin, AddToContextMixin, TemplateView):
    template_name = 'financing/statistics.html'

    def dynamic_context(self):
        tl = Loan.get_approved().count()
        tla = Loan.get_actives(LoanPayment).count()
        ti = Investment.get_approved().count()
        tia = Investment.get_actives(InvestmentPayment).count()
        return {
            'total_count': json.dumps([
                ['Préstamos', Loan.objects.count()],
                ['Inversiónes', Investment.objects.count()],
            ]),
            'total_amount': json.dumps([
                ['Préstamos', float(Loan.objects.all().aggregate(
                    Sum('amount'))['amount__sum'] or 0)],
                ['Inversiónes', float(Investment.objects.all().aggregate(
                    Sum('amount'))['amount__sum'] or 0)],
            ]),
            'avg_amount': json.dumps([
                ['Préstamos',   float(Loan.objects.all().aggregate(
                    Avg('amount'))['amount__avg'] or 0)],
                ['Inversiónes', float(Investment.objects.all().aggregate(
                    Avg('amount'))['amount__avg'] or 0)],
            ]),
            'state': {
                'loan': {
                    'approved': json.dumps([
                        ['Activos', tla],
                        ['Completados', tl - tla],
                    ]),
                    'all': json.dumps([
                        ['Aprobados', tl],
                        ['Rechazados', Loan.get_not_approved().count()],
                        ['Sin revisar', Loan.get_to_check().count()],
                    ])
                },
                'investment': {
                    'approved': json.dumps([
                        ['Activas', tia],
                        ['Completadas', ti - tia],
                    ]),
                    'all': json.dumps([
                        ['Aprobados', ti],
                        ['Rechazados', Investment.get_not_approved().count()],
                        ['Sin revisar', Investment.get_to_check().count()],
                    ])
                },
            },
            'grouped_by_month': json.dumps({
                'loan': {
                    'application': Loan.group_by_month('application_date'),
                    'approved': Loan.group_by_month('approval_date')
                },
                'investment': {
                    'application': Investment.group_by_month('application_date'),
                    'approved': Investment.group_by_month('approval_date')
                }
            })
        }


class FinancingSearchView(LoginEmployeeRequiredMixin, AddToContextMixin, ListView):
    template_name = 'financing/search_finance.html'
    form_class = SearchFinancingForm
    fields = ['code', 'application_date', 'approval_date', 'start_date', 'end_date', 'name',
              'amount', 'interest_rate', 'checked', 'installments_number', 'client__id',
              'client__document', 'client__first_name', 'client__last_name', 'f_type']

    def get_queryset(self):
        """Return the list of items for this view."""
        self.get_model()
        filter_kwargs = {
            'code__icontains': self.request.GET.get('code', '').strip()}
        if self.model is None and filter_kwargs['code__icontains'] != '':
            l = Loan.objects.filter(**filter_kwargs).annotate(f_type=Case(
                default=Value(True), output_field=BooleanField())).values(*self.fields)
            i = Investment.objects.filter(**filter_kwargs).annotate(f_type=Case(
                default=Value(False), output_field=BooleanField())).values(*self.fields)
            return l.union(i)
        if filter_kwargs['code__icontains'] != '':
            return self.model.objects.filter(**filter_kwargs)\
                .annotate(f_type=Case(
                    default=Value(True if type(self.model) is Loan else False),
                    output_field=BooleanField()))\
                .values(*self.fields)
        return Loan.objects.none()

    def get_model(self):
        _type = self.request.GET.get('type', '').lower()
        if _type == 'l':
            self.model = Loan
        elif _type == 'i':
            self.model = Investment
        else:
            self.model = None

    def dynamic_context(self):
        """Return the list of items for this view."""
        return {'form': self.form_class({
            'code': self.request.GET.get('code', '').strip().lower(),
            'type': self.request.GET.get('type', '').strip().lower()
        })}


class FinancingDetailDetailView(LoginRequiredMixin, AccessMixin, DetailView):

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not (self.request.user.is_employee or self.object.client == self.request.user):
            return self.cant_access(self.request)
        today = timezone.now()
        context = self.get_context_data(
            object=self.object,
            payments=(self.payment_class.objects
                      .filter(finance=self.object)
                      .annotate(overdue=Case(
                          When(Q(effective_date=None) & Q(
                              planned_date__lt=today), then=Value(True)),
                          default=Value(False),
                          output_field=BooleanField())
                      )
                      .order_by('planned_date')))
        return self.render_to_response(context)


class LoanDetailView(FinancingDetailDetailView, AddToContextMixin, DetailView):
    model = Loan
    template_name = 'financing/details.html'
    payment_class = LoanPayment
    add_to_context = {'f_type': True}


class InvestmentDetailView(FinancingDetailDetailView, AddToContextMixin, DetailView):
    model = Investment
    template_name = 'financing/details.html'
    payment_class = InvestmentPayment
    add_to_context = {'f_type': False}


class UpdatePaymentView(LoginEmployeeRequiredMixin, AddToContextMixin, UpdateView):
    fields = ('method', 'voucher')
    template_name = 'financing/update_payment.html'
    add_to_context = {
        'submit_text': 'Pagar',
        'title': 'Realizar pago',
        'page_title': 'Realizar pago'
    }

    def form_valid(self, form):
        self.object = form.save()
        self.object.effective_date = timezone.now()
        self.object.save()
        messages.success(self.request, 'Pago realizado exitosamente!')
        return HttpResponseRedirect(reverse_lazy(self.success_url_view, kwargs={'pk': self.object.finance.code}))

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['method'].required = True
        form.fields['voucher'].required = True
        return form


class UpdateLoanPayment(UpdatePaymentView):
    model = LoanPayment
    queryset = model.objects.filter(effective_date=None)
    success_url_view = 'financing:loan_details'


class UpdateInvestmentPayment(UpdatePaymentView):
    model = InvestmentPayment
    queryset = model.objects.filter(effective_date=None)
    success_url_view = 'financing:investment_details'
