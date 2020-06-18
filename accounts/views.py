from django.contrib.auth import authenticate, login, get_user_model
# from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ImproperlyConfigured
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.db.models import Value as V
from django.utils.text import capfirst
from django.urls import reverse_lazy
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    LoginView as _LoginView,
    LogoutView
)
from financing.models import Loan, Investment
from common.mixins import AddToContextMixin
from .forms import SignUpForm, AuthenticationForm, SearchClientNameForm
from .models import User
from .mixins import (
    RedirectAuthenticatedClientMixin,
    LoginEmployeeRequiredMixin,
    LoginAdminRequiredMixin
)

User = get_user_model()


class LoginView(_LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    form_class = AuthenticationForm


class SignupView(RedirectAuthenticatedClientMixin, CreateView):
    """Generic Signup View"""
    template_name = 'general_form.html'  # 'accounts/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('home')
    user_types = User.types
    user_type = None

    def get_user_type(self):
        if self.user_type not in self.user_types:
            raise ImproperlyConfigured(
                f'user_type must be one of {self.user_types}')
        return self.user_type

    def form_valid(self, form):
        form.instance.user_type = self.get_user_type()
        self.object = form.save()
        password = form.cleaned_data.get('password1')
        document = form.cleaned_data.get('username')
        user = authenticate(username=document, password=password)
        login(self.request, user)
        next_page = self.request.GET.get(
            'next', self.request.POST.get('next', None))
        if next_page:
            return HttpResponseRedirect(next_page)
        return HttpResponseRedirect(self.get_success_url())


class SignupClientView(LoginEmployeeRequiredMixin, AddToContextMixin, SignupView):
    """Signup Client View"""
    user_type = User.client_type
    add_to_context = {
        'title': 'Registrar cliente',
        'page_title': 'Registrar cliente',
        'submit_text': 'Registrar',
    }


class SignupEmployeeView(LoginAdminRequiredMixin, AddToContextMixin, SignupView):
    """Signup Employee View"""
    user_type = User.employee_type
    add_to_context = {
        'title': 'Registrar empleado',
        'page_title': 'Registrar empleado',
        'submit_text': 'Registrar',
    }


class MyPasswordResetView(RedirectAuthenticatedClientMixin, PasswordResetView):
    email_template_name = 'accounts/password_reset_email.html'
    template_name = 'accounts/password_reset_form.html'
    success_url = reverse_lazy('accounts:password_reset_done')


class MyPasswordResetDoneView(RedirectAuthenticatedClientMixin, PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class MyPasswordResetConfirmView(RedirectAuthenticatedClientMixin, PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:login')
    post_reset_login = True


class ClientSearchView(LoginEmployeeRequiredMixin, AddToContextMixin, ListView):
    template_name = 'accounts/search_client.html'
    model = User
    form_class = SearchClientNameForm
    login_url = reverse_lazy('accounts:login')

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            clients = self.get_queryset()\
                .values('document', 'first_name', 'last_name', 'phone_number', 'email')
            return JsonResponse({'clients': list(clients), 'ok': True}, status=200)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        name = self.request.GET.get('name', '').strip()
        document = self.request.GET.get('document', '').strip()
        queryset = self.model.objects.filter(user_type=self.model.types[1])
        if document != '':
            return queryset.filter(document__icontains=document)
        if name != '':
            return queryset\
                .annotate(full_name=Concat('first_name', V(' '), 'last_name'))\
                .filter(full_name__icontains=name)
        return self.model.objects.none()

    def dynamic_context(self):
        return {'form': self.form_class({
            'name': self.request.GET.get('name', '').strip(),
            'document': self.request.GET.get('document', '').strip()
        })}


class ClientDetailsView(DetailView):
    model = User
    template_name='accounts/details.html'
    pk_url_kwarg = 'document'
    queryset = User.objects.filter(user_type=User.types[1])

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        document = self.kwargs.get(self.pk_url_kwarg)
        try:
            if document:
                return queryset.filter(document=document).get()
        except queryset.model.DoesNotExist:
            pass
        raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['loans'] = Loan.objects.filter(client=self.object)
        context['investments'] = Investment.objects.filter(client=self.object)
        context['user'] = self.request.user
        return context


# class ProfileView(DetailView):
#     model = User
#     template_name = 'accounts/profile.html'
#     slug_field = 'username'
#     slug_url_kwarg = 'username'
#     context_object_name = 'userObject'
