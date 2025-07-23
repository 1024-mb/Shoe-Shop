from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def cart(request):
    return render(request, 'cart/cart.html')

# Create your views here.
