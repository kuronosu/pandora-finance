from django.contrib.auth import authenticate, login, get_user_model
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import ImproperlyConfigured
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.db.models.functions import Concat
from django.db.models import Value as V
from django.utils.text import capfirst
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    LoginView as _LoginView,
    LogoutView
)
from financing.models import Loan, Investment
from common.mixins import AddToContextMixin
from .models import User
from .forms import (
    SignUpForm,
    AuthenticationForm,
    SearchClientNameForm,
)
from .mixins import (
    RedirectAuthenticatedClientMixin,
    LoginEmployeeRequiredMixin,
    LoginAdminRequiredMixin,
    LoginClientRequiredMixin,
)

User = get_user_model()


class LoginView(_LoginView):
    """View for login."""

    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    form_class = AuthenticationForm


class SignupView(RedirectAuthenticatedClientMixin, CreateView):
    """Generic Signup View."""

    template_name = 'general_form.html'  # 'accounts/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('home')
    user_types = User.types
    user_type = None

    def get_user_type(self):
        """Return the user type."""
        if self.user_type not in self.user_types:
            raise ImproperlyConfigured(
                f'user_type must be one of {self.user_types}')
        return self.user_type

    def form_valid(self, form):
        """Validate the form."""
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
    """View to signup client."""

    user_type = User.client_type
    add_to_context = {
        'title': 'Registrar cliente',
        'page_title': 'Registrar cliente',
        'submit_text': 'Registrar',
    }


class SignupEmployeeView(LoginAdminRequiredMixin, AddToContextMixin, SignupView):
    """View to signup employee."""

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
    """View to search client."""

    template_name = 'accounts/search_client.html'
    model = User
    form_class = SearchClientNameForm

    def get_queryset(self):
        """Return the list of items for this view."""
        name = self.request.GET.get('name', '').strip()
        document = self.request.GET.get('document', '').strip()
        queryset = self.model.objects.filter(
            user_type=self.model.types[1], is_active=True)
        if document != '':
            return queryset.filter(document__icontains=document)
        if name != '':
            return queryset\
                .annotate(full_name=Concat('first_name', V(' '), 'last_name'))\
                .filter(full_name__icontains=name)
        return self.model.objects.none()

    def dynamic_context(self):
        """Return the list of items for this view."""
        return {'form': self.form_class({
            'name': self.request.GET.get('name', '').strip(),
            'document': self.request.GET.get('document', '').strip()
        })}


class ClientDetailsView(LoginEmployeeRequiredMixin, AddToContextMixin, DetailView):
    """View to vizualizate client details."""

    model = User
    template_name = 'accounts/details.html'
    queryset = User.objects.filter(user_type=User.types[1], is_active=True)

    def dynamic_context(self):
        return {
            'loans': Loan.objects.filter(client=self.object),
            'investments': Investment.objects.filter(client=self.object),
            'user': self.request.user
        }


class UpdateClientView(LoginEmployeeRequiredMixin, AddToContextMixin, UpdateView):
    """View to update client."""

    model = User
    template_name = 'general_form.html'
    add_to_context = {
        'title': 'Actualizar cliente',
        'page_title': 'Actualizar cliente',
        'submit_text': 'Actualizar',
    }
    fields = ('document',
              'first_name',
              'last_name',
              'phone_number',
              'email',
              'address1',
              'address2',
              'birthdate')

    def form_valid(self, form):
        messages.success(self.request, 'Actualizado exitosamente!')
        return super().form_valid(form)

    def dynamic_context(self):
        return {'user': self.request.user}


class SelfDetailsView(LoginClientRequiredMixin, AddToContextMixin, DetailView):
    """View to vizualizate loged client details."""

    model = User
    login_url = reverse_lazy('accounts:login')
    template_name = 'accounts/self_details.html'

    def get_object(self, queryset=None):
        return self.request.user

    def dynamic_context(self):
        return {
            'loans': Loan.objects.filter(client=self.object),
            'investments': Investment.objects.filter(client=self.object)
        }


class SelfUpdateView(LoginClientRequiredMixin, AddToContextMixin, UpdateView):
    model = User
    template_name = 'accounts/self_update.html'
    add_to_context = {
        'title': 'Actualizar datos',
        'page_title': 'Actualizar datos',
        'submit_text': 'Actualizar',
        'change_password_error': False,
    }
    fields = ('phone_number',
              'email',
              'address1',
              'address2')

    def dispatch(self, request, *args, **kwargs):
        self.password_form = PasswordChangeForm(request.user)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.will_update_password(request):
            self.process_password_change(request)
            return self.render_to_response(self.get_context_data(form=self._get_form()))
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user

    def _get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(instance=self.request.user, **{
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        })

    def form_valid(self, form):
        messages.success(self.request, 'Actualizado exitosamente!')
        return super().form_valid(form)

    def will_update_password(self, request):
        return request.POST.get('action') == 'update_pass'

    def process_password_change(self, request):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(
                request, 'Su contraseña fue actualizada con éxito!')
        else:
            messages.error(
                request, 'Error al cambiar la contraseña.')
            self._add_to_context(change_password_error=True)
        self.password_form = form

    def dynamic_context(self):
        return {
            'password_form': self.password_form
        }
