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

            description = description + strquantity + NewItem.name[:10] + "... "


        create_order = Order(amount=total, paid=False, 
                            user_id_id=request.user.id,)
        create_order.save()

        for item in cart:
            Priceobj = Clothing.objects.get(product_id=item)
            
            order_item = OrderItem(purchase=create_order,
                                product_id=Priceobj, 
                                quantity=cart[item],
                                purchase_price=Priceobj.price,)

        
            order_item.save()

        total = round(total, 2)

        payment_intent = stripe.PaymentIntent.create(
            amount= int(total*100),
            currency='sgd',
            description=description,
            receipt_email=email,
            automatic_payment_methods={"enabled": True},
            metadata={'order_id': str(create_order.purchase_id)},
            
        )

        client_secret_str = str(payment_intent.client_secret)
        print(type(client_secret_str))

        return JsonResponse({'client_secret': str(client_secret_str),})

    
    else:
        return render(request, 'checkout/checkout.html')

