from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def checkout(request):
    return render(request, "checkout/checkout.html")

# Create your views here.
