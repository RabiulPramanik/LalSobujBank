from typing import Any
from django.contrib import admin
from .models import TransactionModel
from .views import send_email

@admin.register(TransactionModel)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['account', 'amount', 'balance_after_transaction', 'transaction_type', 'loan_approve']

    def save_model(self, request, obj, form, change):
        obj.account.balance += obj.amount
        obj.balance_after_transaction = obj.account.balance
        obj.account.save()
        send_email(obj.account.user, obj.amount, "Loan Aprove", "transactions/email.html", 'Loan Aprove')
        super().save_model(request, obj, form, change)
