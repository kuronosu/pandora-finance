from django.http import HttpResponseRedirect
from django.views.generic.base import ContextMixin
from django.core.exceptions import ImproperlyConfigured
from common.util.querrys import get_client


class SetClientMixin:
    def form_valid(self, form):
        form.instance.client = get_client(form.cleaned_data['document'])
        return super().form_valid(form)


class AddToContextMixin:
    add_to_context = {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.add_to_context)
        context.update(self.dynamic_context())
        return context

    def dynamic_context(self):
        return {}
    
    def _add_to_context(self, **kwargs):
        self.add_to_context.update(kwargs)
