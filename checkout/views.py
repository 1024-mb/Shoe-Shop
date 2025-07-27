from django.shortcuts import render, redirect
from django.conf import settings
import djstripe
import json
import stripe

# Create your views here.
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from djstripe.event_handlers import djstripe_receiver
from djstripe.models import Event, Charge, PaymentMethod
from base.models import Clothing, Order, OrderItem


import stripe

stripe.api_key = 'your_secret_key'




# webhook signing secret: whsec_1709d3d9f617576b171944a41c57eb6ba8e8ac16682a96593015280d92de2763
# path('checkout/', include('checkout.urls'), name='checkout'),
@csrf_exempt
@login_required(login_url='login')
def checkout(request):
    cart = request.session.get('cart', {})
    total = 0

    for item in cart:
        NewItem = Clothing.objects.get(product_id=item)
        total += NewItem.price


    order = Order(request.user.id)
    order_item = OrderItem()

    total = round(total, 2)


    payment_intent = stripe.PaymentIntent.create(
        amount= (total*100),
        currency='sgd',
    )

    return render(request, 'checkout', context={})

@login_required(login_url='login')
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)

    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        # Mark order as paid, update inventory, etc.



