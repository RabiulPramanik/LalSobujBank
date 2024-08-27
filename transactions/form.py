from typing import Any
from django import forms
from .models import TransactionModel

class TransactionForm(forms.ModelForm):
    class Meta:
        model = TransactionModel
        fields = ['amount', 'transaction_type']

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()

    def save(self, commit = True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save(commit)

class DepositForm(TransactionForm):
    def save(self, commit=True):
        self.instance.transaction_type = 1  
        return super().save(commit)
    
    def clean_amount(self):
        min_deposit_amount = 100
        amount = self.cleaned_data.get('amount')
        if amount < min_deposit_amount:
            raise forms.ValidationError(f'You need to deposit at least {min_deposit_amount}$')
        return amount

class WithdrawForm(TransactionForm):
    def save(self, commit=True):
        self.instance.transaction_type = 2  
        return super().save(commit)
    
    def clean_amount(self):
        account = self.account
        min_withdraw_amount = 500
        max_withdraw_amount = 20000
        balance = account.balance
        amount = self.cleaned_data.get('amount')
        if amount < min_withdraw_amount:
            raise forms.ValidationError(f'You can withdraw at least {min_withdraw_amount}')
        if amount > max_withdraw_amount:
            raise forms.ValidationError(f'You can withdraw at most {max_withdraw_amount}')
        if amount > balance:
            raise forms.ValidationError(
                f'You have {balance}$ in your account. You cannot withdraw more than your account balance.'
            )
        return amount

class LoanForm(TransactionForm):
    def save(self, commit=True):
        self.instance.transaction_type = 3  
        return super().save(commit)
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        return amount
    
class TransferMoneyForm(forms.Form):
    receiver_account_no = forms.IntegerField()
    amount = forms.IntegerField()


    # def save(self, commit=True):
    #     self.instance.transaction_type = 5  
    #     return super().save(commit)
    
    # def clean_amount(self):
    #     amount = self.cleaned_data.get('amount')
    #     return amount
    # recevier_account_id = forms.IntegerField()
        
        
