from django.urls import path

from . import views

app_name = 'financing'

urlpatterns = [
    path('create/loan', views.CreateLoan.as_view(), name='create_loan'),
    path('create/investment', views.CreateInvestment.as_view(), name='create_investment'),
]
