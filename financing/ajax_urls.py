
from django.urls import path

from . import ajax_views

app_name = 'financing'

urlpatterns = [
    path('guarantees/', ajax_views.user_guarantees, name='user_guarantees'),
    path('filter_financing/', ajax_views.filter_financing, name='filter_financing')
]
