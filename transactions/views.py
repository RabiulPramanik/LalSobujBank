from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import TransactionModel
from .form import DepositForm, WithdrawForm, LoanForm, TransferMoneyForm
from .constants import DEPOSIT, WITHDRAW, LOAN, LOAN_PAID, SEND, RECEIVE
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime
from django.db.models import Sum
from django.views import View
from django.urls import reverse_lazy
from accounts.models import UserBankAccount
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string


def send_email(user, amount, mail_subject, mail_template, title):
    message = render_to_string(mail_template, {
        'user': user,
        'amount': amount,
        'title':title,
    })
    to_Email = user.email
    send_Email = EmailMultiAlternatives(mail_subject, '', to=[to_Email])
    send_Email.attach_alternative(message, "text/html")
    send_Email.send()



class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    model = TransactionModel
    template_name = 'transactions/transactions.html'
    success_url = reverse_lazy("report")
    title = ''

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title
        })
        return context
    
class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title = 'Deposit'

    def get_initial(self):
        initial = {'transaction_type': DEPOSIT}
        return initial

    def form_valid(self, form):
        print("valid Robiul")
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance += amount
        account.save(
            update_fields = [
                'balance'
            ]
        )
        messages.success(self.request, f'{amount}$ was deposited to your account successfully')

        send_email(self.request.user, amount, "Deposite", "transactions/email.html", 'Deposite')

        return super().form_valid(form)
    
    def form_invalid(self, form):
        print("robiul")
        print("Form errors:", form.errors)
        return super().form_invalid(form)
        
    

class WithdrawView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Withdraw'

    def get_initial(self):
        initial = {'transaction_type': WITHDRAW}
        return initial
    def form_valid(self, form):
        print("withdraw")
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance -= amount
        account.save(
            update_fields = [
                'balance'
            ]
        )
        messages.success(self.request, f'{amount}$ was withdraw to your account successfully')
        send_email(self.request.user, amount, "Withdraw", "transactions/email.html", 'Withdraw')
        return super().form_valid(form)


class LoanRequestView(TransactionCreateMixin):
    form_class = LoanForm
    title = 'Request for Loan'

    def get_initial(self):
        initial = {'transaction_type':LOAN}
        return initial
    def form_valid(self, form):
        print("Loan")
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        loan_request_cont = TransactionModel.objects.filter(account = account, transaction_type = 3, loan_approve = True)
        if loan_request_cont.count() >= 3:
            return HttpResponse("You have cross the loan limits")
        messages.success(
            self.request,
            f'Loan request for {amount}$ submitted successfully'
        )
        send_email(self.request.user, amount, "Loan request", "transactions/email.html", 'Loan request')
        return super().form_valid(form)

class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = 'transactions/report.html'
    model = TransactionModel
    balance = 0
    

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account = self.request.user.account
        )
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            queryset = queryset.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)
            self.balance = TransactionModel.objects.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date).aggregate(total=Sum('amount')).get('total', 0)
        else:
            self.balance = self.request.user.account.balance
        
        return queryset.distinct()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account,
            'title' : 'Report'
        })

        return context

class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(TransactionModel, id=loan_id)
        
        if loan.loan_approve:
            print("robiul")
            user_account = loan.account

            if loan.amount <= user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.loan_approved = True
                loan.transaction_type = LOAN_PAID
                loan.save()
                return redirect("loan_list")
            else:
                messages.error(self.request, f'Loan amount is greater than available balance')
        return redirect("loan_list")

class LoanListView(LoginRequiredMixin, ListView):
    model = TransactionModel
    template_name = 'transactions/loan_list.html'
    context_object_name = 'loans'
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = 'Loan List'
        return context
    

    def get_queryset(self):
        user_account = self.request.user.account
        queryset = TransactionModel.objects.filter(account = user_account,transaction_type=3)
        return queryset



# class TransferMoneyView(CreateView):
#     template_name = ''
#     model = TransactionModel
#     form_class = TransferMoneyForm
#     success_url = reverse_lazy("report")
#     def form_valid(self, form):
#         print(form.cleaned_data)
#         return super().form_valid(form)
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["title"] = 'Transfer Money'
#         return context
def TransferMoneyView(request):
    if request.method == "POST":
        form = TransferMoneyForm(request.POST)
        if form.is_valid():
            account_no = form.cleaned_data['receiver_account_no']
            try:
                account = UserBankAccount.objects.get(account_no=account_no)
            except UserBankAccount.DoesNotExist:
                form.add_error('receiver_account_no', 'Account not found!')
            else:
                amount = form.cleaned_data['amount']

                # Check if the user has sufficient balance
                if request.user.account.balance < amount:
                    form.add_error('amount', 'Insufficient funds.')
                elif request.user.account.account_no == account.account_no:
                    form.add_error('receiver_account_no', 'This is your account No')
                else:
                    # Perform the transfer
                    request.user.account.balance -= amount
                    request.user.account.save()
                    TransactionModel.objects.create(
                        account = request.user.account,
                        amount = -amount,
                        balance_after_transaction = request.user.account.balance,
                        transaction_type = SEND,
                    )

                    account.balance += amount
                    account.save()
                    TransactionModel.objects.create(
                        account = account,
                        amount = amount,
                        balance_after_transaction = account.balance,
                        transaction_type = RECEIVE,
                    )
                    send_email(request.user, amount, "Transfer Loan", "transactions/email.html", 'Transfer Loan')
                    send_email(account.user, amount, "Receive Loan", "transactions/email.html", 'Receive Loan')

                    return redirect("report")
    else:
        form = TransferMoneyForm()

    return render(request, "money.html", {'form': form, 'title': 'Transfer Money'})
    

    
    
     
    
    
