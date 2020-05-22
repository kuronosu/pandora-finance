from django.core.exceptions import ImproperlyConfigured
from common.util.querrys import get_client


class SetClientMixin:
    def form_valid(self, form):
        form.instance.client = get_client(form.cleaned_data['document'])
        return super().form_valid(form)


class GeneralFormContexMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if (not hasattr(self, 'title') or not hasattr(self, 'page_title')
                or not hasattr(self, 'submit_text')):
            raise ImproperlyConfigured(
                'GeneralFormContexMixin need title, page_title, submit_text attributes')
        context['title'] = self.title
        context['page_title'] = self.page_title
        context['submit_text'] = self.submit_text
        return context
