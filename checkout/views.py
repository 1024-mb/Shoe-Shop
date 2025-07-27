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
from base.models import Clothing, Order, OrderItem, User


import stripe
import os
from django.http import JsonResponse

stripe.api_key = os.getenv('stripekey')




# webhook signing secret: 
# path('checkout/', include('checkout.urls'), name='checkout'),
@csrf_exempt
@login_required(login_url='login')
def checkout(request):
    if request.method=='POST':
        Address = request.POST.get('AddressLine1')
        City = request.POST.get('City')
        PostCode = request.POST.get('PostCode')

        cart = request.session.get('cart', {})
        total = 0
        description = ''

        user = User.objects.get(id=request.user.id)
        email = user.email

        for item in cart:
            strquantity = str(cart[item])
            NewItem = Clothing.objects.get(product_id=item)
            total += NewItem.price

            description = description + strquantity + NewItem.name[:5]


        create_order = Order(amount=total, paid=False, 
                            user_id_id=request.user.id)
        create_order.save()
        
        for item in cart:
            Priceobj = Clothing.objects.get(product_id=item)
            
            order_item = OrderItem(purchase=create_order,
                                product_id=Priceobj, 
                                quantity=cart[item],
                                purchase_price=Priceobj,)

        
            order_item.save()


        total = round(total, 2)

        payment_intent = stripe.PaymentIntent.create(
            amount= int(total*100),
            currency='sgd',
            description=description,
            receipt_email=email,
            automatic_payment_methods={"enabled": True}
        )

        return JsonResponse({'client_secret': payment_intent.client_secret}), render(request, 'checkout/checkout.html')
    
    else:
        return render(request, 'checkout/checkout.html')


@login_required(login_url='login')
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = stripe.Webhook.construct_event(payload, sig_header, 'whsec_1709d3d9f617576b171944a41c57eb6ba8e8ac16682a96593015280d92de2763')

    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        # Mark order as paid, update inventory, etc.



