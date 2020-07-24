
from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), {'next_page': '/'}, name='logout'),
    path('signup/client/', views.SignupClientView.as_view(), name='signup_client'),
    path('signup/employee/', views.SignupEmployeeView.as_view(), name='signup_employee'),
    path('terminate/employee/', views.TerminateEmployeeView.as_view(), name='terminate_employee'),
    path('account/', views.SelfDetailsView.as_view(), name='self_details'),
    path('account/update/', views.SelfUpdateView.as_view(), name='self_update'),
    path('clients/', views.ClientSearchView.as_view(), name='search_client'),
    path('clients/<str:pk>/', views.ClientDetailsView.as_view(), name='client_details'),
    path('clients/<str:pk>/update/', views.UpdateClientView.as_view(), name='update_client'),
    path('clients/<str:pk>/unsubscribe/', views.UnsubscribeClientView.as_view(), name='unsubscribe_client'),
]
