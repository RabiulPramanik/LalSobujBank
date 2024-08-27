from django.urls import path
from . import views

urlpatterns = [
    path('deposit/', views.DepositMoneyView.as_view(), name="deposit"),
    path('withdraw/', views.WithdrawView.as_view(), name="withdraw"),
    path('loanrequest/', views.LoanRequestView.as_view(), name="loanrequest"),
    path('report/', views.TransactionReportView.as_view(), name="report"),
    path('loans/', views.LoanListView.as_view(), name="loan_list"),
    path('loans/<int:loan_id>/', views.PayLoanView.as_view(), name="loan_paid"),
    path('transfer_money/', views.TransferMoneyView, name="transfer_money"),
    # path('transfer_money/', views.TransferMoneyView.as_view(), name="transfer_money"),
]

