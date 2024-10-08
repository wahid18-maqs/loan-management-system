from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import LoanRequestForm, LoanTransactionForm
from .models import loanRequest, loanTransaction, CustomerLoan
from django.db.models import Sum
from django.http import HttpResponseRedirect, HttpResponse

# @login_required(login_url='/account/login-customer')
def home(request):
    return render(request, 'home.html', context={})

@login_required(login_url='/account/login-customer')
def LoanRequest(request):
    form = LoanRequestForm()

    if request.method == 'POST':
        form = LoanRequestForm(request.POST)

        if form.is_valid():
            loan_obj = form.save(commit=False)
            loan_obj.customer = request.user.customer
            loan_obj.save()
            return redirect('/')
    
    return render(request, 'loanApp/loanrequest.html', context={'form': form})

@login_required(login_url='/account/login-customer')
def LoanPayment(request):
    form = LoanTransactionForm()
    
    if request.method == 'POST':
        form = LoanTransactionForm(request.POST)
        
        if form.is_valid():
            payment = form.save(commit=False)
            payment.customer = request.user.customer
            payment.save()
            return redirect('/')
    
    return render(request, 'loanApp/payment.html', context={'form': form})

@login_required(login_url='/account/login-customer')
def UserTransaction(request):
    transactions = loanTransaction.objects.filter(customer=request.user.customer)
    return render(request, 'loanApp/user_transaction.html', context={'transactions': transactions})

@login_required(login_url='/account/login-customer')
def UserLoanHistory(request):
    loans = loanRequest.objects.filter(customer=request.user.customer)
    return render(request, 'loanApp/user_loan_history.html', context={'loans': loans})

@login_required(login_url='/account/login-customer')
def UserDashboard(request):
    requestLoan = loanRequest.objects.filter(customer=request.user.customer).count()
    approved = loanRequest.objects.filter(customer=request.user.customer, status='approved').count()
    rejected = loanRequest.objects.filter(customer=request.user.customer, status='rejected').count()

    totalLoan = CustomerLoan.objects.filter(customer=request.user.customer).aggregate(Sum('total_loan'))['total_loan__sum'] or 0
    totalPayable = CustomerLoan.objects.filter(customer=request.user.customer).aggregate(Sum('payable_loan'))['payable_loan__sum'] or 0
    totalPaid = loanTransaction.objects.filter(customer=request.user.customer).aggregate(Sum('payment'))['payment__sum'] or 0

    context = {
        'request': requestLoan,
        'approved': approved,
        'rejected': rejected,
        'totalLoan': totalLoan,
        'totalPayable': totalPayable,
        'totalPaid': totalPaid
    }

    return render(request, 'loanApp/user_dashboard.html', context=context)

def error_404_view(request, exception):
    print("Page not found")
    return render(request, 'notFound.html')
