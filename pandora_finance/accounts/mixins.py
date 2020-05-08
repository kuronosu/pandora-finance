from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import AccessMixin


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
        return super(RedirectAuthenticatedClientMixin, self).dispatch(request, *args, **kwargs)


class LoginEmployeeRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated and is employee."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/')
        if not self.request.user.is_employee:
            return HttpResponseRedirect('/')
        return super().dispatch(request, *args, **kwargs)


class LoginAdminRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated and is admin."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/')
        if not self.request.user.is_superuser:
            return HttpResponseRedirect('/')
        return super().dispatch(request, *args, **kwargs)
