
from django.urls import path, include
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # path('', include('accounts.urls', namespace='accounts')),
    path('accounts/', include('accounts.ajax_urls', namespace='ajax_accounts')),
    path('financing/', include('financing.ajax_urls', namespace='ajax_financing')),
]
