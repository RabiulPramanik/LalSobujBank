from django.db import models
from accounts.models import UserBankAccount
from .constants import TRANSACTION_TYPES

class TransactionModel(models.Model):
    account = models.ForeignKey(UserBankAccount, related_name="transaction", on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    balance_after_transaction = models.DecimalField(decimal_places=2, max_digits=12)
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPES, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    loan_approve = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.amount} {self.transaction_type} by {str(self.account.account_no)}'

    class Meta:
        ordering = ['timestamp']
