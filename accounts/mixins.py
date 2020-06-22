from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin


class RedirectAuthenticatedClientMixin:
    def dispatch(self, request, *args, **kwargs):
        if hasattr(self, 'request'):
            if self.request.user.is_authenticated and self.request.user.is_client:
                return HttpResponseRedirect('/')
        return super(RedirectAuthenticatedClientMixin, self).dispatch(request, *args, **kwargs)


class RedirectAuthenticatedMixin:
    def dispatch(self, request, *args, **kwargs):
        if hasattr(self, 'request'):
            if self.request.user.is_authenticated:
                return HttpResponseRedirect('/')
        return super(RedirectAuthenticatedMixin, self).dispatch(request, *args, **kwargs)


class EmployeeRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_employee:
            return HttpResponseRedirect('/')
        return super().dispatch(request, *args, **kwargs)


class LoginEmployeeRequiredMixin(LoginRequiredMixin, EmployeeRequiredMixin):
    """Verify that the current user is authenticated and is employee."""


class AdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            return HttpResponseRedirect('/')
        return super().dispatch(request, *args, **kwargs)


class LoginAdminRequiredMixin(LoginRequiredMixin, AdminRequiredMixin):
    """Verify that the current user is authenticated and is admin."""


class __CanApproveMixin:
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.can_approve:
            return HttpResponseRedirect('/')
        return super().dispatch(request, *args, **kwargs)


class CanApproveMixin(LoginRequiredMixin, __CanApproveMixin):
    """Verify that the current user is authenticated and can approve financings."""
