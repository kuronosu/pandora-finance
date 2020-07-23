from django.urls import path

from . import views

app_name = 'financing'

urlpatterns = [
    path('create/loan/', views.CreateLoanView.as_view(), name='create_loan'),
    path('create/investment/', views.CreateInvestmentView.as_view(), name='create_investment'),
    path('create/guarantee/', views.CreateGuaranteeView.as_view(), name='create_guarantee'),
    path('create/guarantee/type/', views.CreateGuaranteeTypeView.as_view(), name='create_guarantee_type'),
    path('approve/', views.FinancingApproveListView.as_view(), name='aprove'),
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),
    path('search/', views.FinancingSearchView.as_view(), name='search'),
    path('l/<str:pk>/', views.LoanDetailView.as_view(), name='loan_details'),
    path('i/<str:pk>/', views.InvestmentDetailView.as_view(), name='investment_details'),
]
