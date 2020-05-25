from django.contrib.auth import authenticate, login, get_user_model
# from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ImproperlyConfigured
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.http import HttpResponseRedirect
from django.utils.text import capfirst
from django.urls import reverse_lazy
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    LoginView as _LoginView,
    LogoutView
)

from common.mixins import AddToContextMixin
from .forms import SignUpForm, AuthenticationForm, UserModel
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


# class ProfileView(DetailView):
#     model = User
#     template_name = 'accounts/profile.html'
#     slug_field = 'username'
#     slug_url_kwarg = 'username'
#     context_object_name = 'userObject'
