from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def checkout(request):
    return render(request, "checkout/checkout.html")

# Create your views here.
