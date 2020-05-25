
from django.urls import path

from . import ajax_views

app_name = 'accounts'

urlpatterns = [
    path('search/user/', ajax_views.search_user, name='search_user'),
]
