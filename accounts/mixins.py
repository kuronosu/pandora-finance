from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin


class RedirectAuthenticatedClientMixin:
    def dispatch(self, request, *args, **kwargs):
        if hasattr(self, 'request'):
            if self.request.user.is_authenticated and self.request.user.is_client:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        return super(RedirectAuthenticatedClientMixin, self).dispatch(request, *args, **kwargs)


class RedirectAuthenticatedMixin:
    def dispatch(self, request, *args, **kwargs):
        if hasattr(self, 'request'):
            if self.request.user.is_authenticated:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        return super(RedirectAuthenticatedMixin, self).dispatch(request, *args, **kwargs)


class EmployeeRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_employee:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        return super().dispatch(request, *args, **kwargs)


class LoginEmployeeRequiredMixin(LoginRequiredMixin, EmployeeRequiredMixin):
    """Verify that the current user is authenticated and is employee."""


class AdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        return super().dispatch(request, *args, **kwargs)


class LoginAdminRequiredMixin(LoginRequiredMixin, AdminRequiredMixin):
    """Verify that the current user is authenticated and is admin."""


class CanApproveMixin:
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.can_approve:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        return super().dispatch(request, *args, **kwargs)


class ChiefCreditLoginRequiredMixin(LoginRequiredMixin, EmployeeRequiredMixin, CanApproveMixin):
    """Verify that the current user is authenticated and can approve financings."""


class ClientRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_client:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        return super().dispatch(request, *args, **kwargs)


class LoginClientRequiredMixin(LoginRequiredMixin, ClientRequiredMixin):
    """Verify that the current user is authenticated and is a client."""