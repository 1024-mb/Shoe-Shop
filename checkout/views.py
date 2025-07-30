from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
import djstripe
import json
import stripe
from geopy.geocoders import *

# Create your views here.
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


from djstripe.models import Event, Charge, PaymentMethod
from base.models import Clothing, Order, OrderItem, User

import time
import hmac
import hashlib
import stripe
import os
import requests
import uuid

stripe.api_key = os.getenv('stripekey')
api_secret = os.getenv('api_secret_lalamove')
api_key = os.getenv('api_key_lalamove')

def create_quotation(latitude, longitude, location_address, Name, Number):

    url = "https://rest.sandbox.lalamove.com/v3/quotations"
    method = "POST"
    path = "/v3/quotations"
    timestamp = str(int(time.time() * 1000))

    body = {
        "data": {
            "quotationId": "1514140994227007571",
            "sender": {
                "name": "Moiz",
                "phone": "1234567890"
            },
            "recipient": {
                "name": "Recipient Name",
                "phone": "0987654321"
            },
            "remarks": "Please handle with care",
            "isPODEnabled": False
        }
    }

    raw_signature = f"{timestamp}\r\n{method}\r\n{path}\r\n\r\n{json.dumps(body)}"
    signature = hmac.new(
        api_secret.encode('utf-8'),
        raw_signature.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    token = f"{api_key}:{timestamp}:{signature}"

    headers = {
    "Authorization": f"hmac {token}",
    "Market": "SG",  # Change to your market code
    "Content-Type": "application/json",
    "Request-ID": str(uuid.uuid4())
    }

    response = requests.post(
        "https://rest.sandbox.lalamove.com/v3/orders",
        headers=headers,
        json=body
    )


def place_order(api_key, api_secret, quotation_id, stop_ids):
    url = "https://rest.sandbox.lalamove.com/v3/orders"
    method = "POST"
    path = "/v3/orders"

    body = {
        "data": {
            "quotationId": quotation_id,
            "sender": {
                "stopId": stop_ids[0],
                "name": "Sender Name",
                "phone": "+60123456789"
            },
            "recipients": [
                {
                    "stopId": stop_ids[1],
                    "name": "Recipient Name",
                    "phone": "+60198765432"
                }
            ]
        }
    }

    body_json = json.dumps(body)
    timestamp, signature = generate_signature(api_secret, method, path, body_json)
    headers = {
        "Authorization": f"hmac {api_key}:{timestamp}:{signature}",
        "Market": "MY",
        "Content-Type": "application/json",
        "Request-ID": "unique-request-id-456"
    }

    response = requests.post(url, headers=headers, data=body_json)
    return response.json()

def generate_signature(secret, method, path, body):
    timestamp = str(int(time.time() * 1000))
    raw_signature = f"{timestamp}\r\n{method}\r\n{path}\r\n\r\n{body}"
    signature = hmac.new(secret.encode(), raw_signature.encode(), hashlib.sha256).hexdigest()
    return timestamp, signature

@csrf_exempt
@login_required(login_url='login')
def checkout(request):
    order_id = request.session.get('order_id')
    items_list = []
    description = ''

    if request.method=='POST':
        address = request.POST.get('address-input')
        phone = request.POST.get('phone')

        print(phone)
        print(address)

        email = request.user.email
        
        """
                location_address = address1 + ', ' + address2
                print(location_address)

                loc = Nominatim(user_agent="Geopy Library")

                # entering the location name
                location = loc.geocode(postcode + ', Singapore')

                latitude = location.latitude
                longitude = location.longitude
                print(latitude)
                print(longitude)

                ret = create_quotation(latitude, longitude, location_address)
                print(ret)

        """       

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
