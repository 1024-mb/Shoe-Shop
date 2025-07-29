from django.shortcuts import render, redirect
from django.conf import settings
import djstripe
import json
import stripe

# Create your views here.
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


from djstripe.models import Event, Charge, PaymentMethod
from base.models import Clothing, Order, OrderItem, User


import stripe
import os
from django.http import JsonResponse

stripe.api_key = os.getenv('stripekey')

@csrf_exempt
@login_required(login_url='login')
def checkout(request):
    order_id = request.session.get('order_id')
    items_list = []
    description = ''

    if request.method=='POST':
        Address = request.POST.get('AddressLine1')
        City = request.POST.get('City')
        PostCode = request.POST.get('PostCode')
        email = request.user.email

        items = OrderItem.objects.filter(order_id=order_id)
        order = Order.objects.get(purchase_id=order_id)

        total = round(float(order.amount), 2)

        for item in items:
            strquantity = str(item.quantity)
            NewItem = Clothing.objects.get(product_id=item)

            description = description + strquantity + ' ' + NewItem.name[:20] + "... "


        payment_intent = stripe.PaymentIntent.create(
            amount= int(total*100),
            currency='sgd',
            description=description,
            receipt_email=email,
            payment_method_types=['card'],
            automatic_payment_methods={'enabled': False},
            metadata={"order_id": order_id},)

        client_secret_str = str(payment_intent.client_secret)

        return JsonResponse({'client_secret': str(client_secret_str)})
    

    else:
        order = Order.objects.get(purchase_id=order_id.replace('-', ''))

        total = round(int(order.amount), 2)

        items = OrderItem.objects.filter(order_id=order_id)

        for item in items:
            product_id = item.product_id
            print(product_id)
            stock_item = Clothing.objects.filter(product_id=product_id)
            stock = stock_item.stock

            items_list.append([item, item.quantity, stock])

        return render(request, 'checkout/checkout.html', context={'items': items_list,
                                                                  'total': total})


@login_required(login_url='login')
def payment_succeeded(request):
    return render(request, 'checkout/payment_succeeded.html')

@login_required(login_url='login')
def payment_failed(request):
    return render(request, 'checkout/payment_failed.html')
