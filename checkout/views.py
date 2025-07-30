from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
import djstripe
import json
import stripe
from geopy.geocoders import *

# Create your views here.
from django.contrib import messages
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
import random

stripe.api_key = os.getenv('stripekey')
api_secret = os.getenv('api_secret_lalamove')
api_key = os.getenv('api_key_lalamove')

def create_quotation(latitude, longitude, location_address, quantity):
    url = "https://rest.sandbox.lalamove.com/v3/quotations"
    method = "POST"
    path = "/v3/quotations"
    timestamp = str(int(time.time() * 1000))
    weight = (quantity * 0.5) + 0.5

    if weight > 8:
        service = 'CAR'

    else:
        service = 'MOTORCYCLE'

    weight = str(weight)

    body = {
        "data": {
            "serviceType": service,
            "language": "en_SG",
            "stops": [
                {
                    "coordinates": {
                        "lat": "1.304833",
                        "lng": "103.831833"
                    },
                    "address": "Midpoint Mall, Orchard"
                },
                {
                    "coordinates": {
                        "lat": str(latitude),
                        "lng": str(longitude)
                    },
                    "address": str(location_address)
                }
            ],
            "item": {
                "quantity": str(quantity),
                "weight": f"LESS_THAN_{weight}KG",
                "categories": ["SHOES", "CLOTHES", "WEARABLE_ACCESSORIES"],
                "handlingInstructions": ["KEEP_UPRIGHT"]
            }
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
        "Market": "SG",
        "Content-Type": "application/json",
        "Request-ID": str(uuid.uuid4())
    }

    # ✅ Send the request
    response = requests.post(url, headers=headers, json=body)

    # ✅ Handle the response
    if response.status_code == 201:
        print('97')
        return response.json()  # Parsed JSON response
    
    else:
        print("Error:", response.status_code, response.text)
        return None

def place_order(api_key, api_secret, quotation_id, stop_ids, name, number, order_id):
    url = "https://rest.sandbox.lalamove.com/v3/orders"
    method = "POST"
    path = "/v3/orders"

    body = {
        "data": {
            "quotationId": quotation_id,
            "sender": {
                "stopId": stop_ids[0],
                "name": "Moiz",
                "phone": "+6598367954"
            },
            "recipients": [
                {
                    "stopId": stop_ids[1],
                    "name": name,
                    "phone": number.replace(' ', ''),
                }
            ],
            "metadata": {
                "order_id": order_id,
                "institution": "Heat Sneakers"
            }
        }
    }

    body_json = json.dumps(body)
    timestamp, signature = generate_signature(api_secret, method, path, body_json)
    headers = {
        "Authorization": f"hmac {api_key}:{timestamp}:{signature}",
        "Market": "SG",
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

    quantityObj = OrderItem.objects.filter(purchase_id=order_id)
    quantity = 0

    for item in quantityObj:
        quantity += item.quantity

    items_list = []
    description = ''

    if request.method=='POST':
        address = request.POST.get('address-input')
        postcode = request.POST.get('postcode')
        phone = request.POST.get('phone')

        print(postcode)
        print(address)
        print(phone)



        email = request.user.email
        
        loc = Nominatim(user_agent="Geopy Library")

        # entering the location name
        location = loc.geocode(postcode + ', Singapore')

        latitude = location.latitude
        longitude = location.longitude

        
        quotation = create_quotation(latitude, longitude, address, quantity)

        if quotation:
            quotation_id = quotation['data']
            quotation_id = quotation_id['quotationId']

            stop_ids = []

            stops = quotation['data']['stops']
            for item in stops:
                stop_ids.append(item['stopId'])

            id = request.session.get('order_id')

            order = place_order(api_key, api_secret, quotation_id, stop_ids,
                                request.user.first_name+' '+request.user.last_name,phone, id)

            print(order)

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

            return JsonResponse({'client_secret': str(client_secret_str),
                                'quotation': quotation})
    
        else:
            messages.error(request, 'Sorry, We are unable to process your order at the moment. Please try again later')

    else:
        order = Order.objects.get(purchase_id=order_id.replace('-', ''))

        total = round(int(order.amount), 2)

        items = OrderItem.objects.filter(order_id=order_id)

        for item in items:
            product_id = item.product_id
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
