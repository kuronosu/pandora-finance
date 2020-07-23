from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin


class AccessMixin:
    force_index_redirect = False

    def cant_access(self, request):
        redirect_to = request.META.get('HTTP_REFERER', '/')
        if self.force_index_redirect or str(reverse_lazy('accounts:login')) in redirect_to:
            return HttpResponseRedirect('/')
        return HttpResponseRedirect(redirect_to)

    def can_access(self, handle, *args, **kwargs):
        return handle(*args, **kwargs)


class RedirectAuthenticatedClientMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if hasattr(self, 'request'):
            if self.request.user.is_authenticated and self.request.user.is_client:
                return self.cant_access(request)
        return self.can_access(super().dispatch, *[request, *args], **kwargs)


class RedirectAuthenticatedMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if hasattr(self, 'request'):
            if self.request.user.is_authenticated:
                return self.cant_access(request)
        return self.can_access(super().dispatch, *[request, *args], **kwargs)


class EmployeeRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_employee:
            return self.cant_access(request)
        return self.can_access(super().dispatch, *[request, *args], **kwargs)


class LoginEmployeeRequiredMixin(LoginRequiredMixin, EmployeeRequiredMixin):
    """Verify that the current user is authenticated and is employee."""


class AdminRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            return self.cant_access(request)
        return self.can_access(super().dispatch, *[request, *args], **kwargs)


class LoginAdminRequiredMixin(LoginRequiredMixin, AdminRequiredMixin):
    """Verify that the current user is authenticated and is admin."""


class CanApproveMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.can_approve:
            return self.cant_access(request)
        return self.can_access(super().dispatch, *[request, *args], **kwargs)


class ChiefCreditLoginRequiredMixin(LoginRequiredMixin, EmployeeRequiredMixin, CanApproveMixin):
    """Verify that the current user is authenticated and can approve financings."""


class ClientRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_client:
            return self.cant_access(request)
        return self.can_access(super().dispatch, *[request, *args], **kwargs)


class LoginClientRequiredMixin(LoginRequiredMixin, ClientRequiredMixin):
    """Verify that the current user is authenticated and is a client."""
