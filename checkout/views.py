from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
import djstripe
import json
import stripe
from geopy.geocoders import *

import phonenumbers

# Create your views here.
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

import time

from djstripe.models import Event, Charge, PaymentMethod
from base.models import Clothing, Order, OrderItem, User, ProductVariant

from datetime import datetime
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
    weight = (quantity * 1.5) + 0.5

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
                    "address": "Midpoint Mall, 220 Orchard Road, Orchard"
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
                "handlingInstructions": ["KEEP_DRY"]
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
        print(response.json())
        return response.json()  # Parsed JSON response
    
    else:
        return None

def place_order(api_key, api_secret, quotation_id, stop_ids, name, number, order_id):
    request_id = str(uuid.uuid4())
    

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
                    "remarks": "HeatSneakers Clothing & Apparel delivery"
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
        "Request-ID": request_id
    }

    response = requests.post(url, headers=headers, data=body_json)
    if response.status_code == 201:
        print(response.json())
        return response.json()  # Parsed JSON response
    
    else:
        print("Error:", response.status_code, response.text)
        return None


def generate_signature(secret, method, path, body):
    timestamp = str(int(time.time() * 1000))
    raw_signature = f"{timestamp}\r\n{method}\r\n{path}\r\n\r\n{body}"
    signature = hmac.new(secret.encode(), raw_signature.encode(), hashlib.sha256).hexdigest()
    return timestamp, signature

@csrf_exempt
@login_required(login_url='login')
def checkout(request):
    if request.session.get('order_id', None) != None:
        order_id = request.session.get('order_id').replace('-', '')

        order = None
        check = None
        items_list = []
        description = ''

        order = Order.objects.get(purchase_id=order_id)

        if request.method == 'POST':
            address = request.POST.get('address-input')
            postcode = request.POST.get('postcode')
            phone = request.POST.get('phone')
            email = request.user.email

            loc = Nominatim(user_agent="Geopy Library")

            # entering the location name
            location = loc.geocode(postcode + ', Singapore')

            if location != None:
                latitude = location.latitude
                longitude = location.longitude

            else:
                messages.error(request, 'Error: invalid address')
                return redirect('checkout')

            items = OrderItem.objects.filter(purchase_id=order_id)
            quantity = 0

            for item in items:
                quantity += item.quantity
            
            quotation = create_quotation(latitude, longitude, address, quantity)

            try:
                if not(phonenumbers.is_valid_number(phonenumbers.parse(phone, "SG"))):
                    total = round(float(order.amount), 2)
                    items = OrderItem.objects.filter(purchase_id=order_id)

                    for item in items:
                        items_list.append([item, item.quantity, str(item.product_id_id), 
                                           item.purchase_price, item.purchase_price * item.quantity])

                    print('266')
                    messages.error(request, 'invalid phone number')
                    return redirect('checkout')

            except:
                messages.error(request, 'invalid phone number')
                return redirect('checkout')


            if quotation:
                quotation_id = quotation['data']
                quotation_id = quotation_id['quotationId']

                stop_ids = []
                stops = quotation['data']['stops']

                for item in stops:
                    stop_ids.append(item['stopId'])

                id = request.session.get('order_id')

                order = place_order(api_key, api_secret, quotation_id, stop_ids,
                                    request.user.first_name+' '+request.user.last_name, phone, id)

                if order:
                    request.session['request_id'] = str(uuid.uuid4())

                    items = OrderItem.objects.filter(purchase_id=order_id)
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
                        automatic_payment_methods={'enabled': True},
                        metadata={"order_id": order_id},)

                    client_secret_str = str(payment_intent.client_secret)

                    
                    print('250')
                    return JsonResponse({'client_secret': str(client_secret_str),
                                        'quotation': quotation})
        
                else:
                    messages.error(request, 'Sorry, we are unable to process your order at the moment.')
                    return redirect('cart')

            else:
                messages.error(request, 'Sorry, we are unable to process your order at the moment.')
                return redirect('cart')

        else:
            total = round(float(order.amount), 2)
            items = OrderItem.objects.filter(purchase_id=order_id)

            for item in items:
                items_list.append([item, item.quantity, str(item.product_id_id), item.purchase_price, item.purchase_price * item.quantity])

            print('266')
            return render(request, 'checkout/checkout.html', context={'items': items_list, 'total': total})

    else:
        return redirect('cart')

@csrf_exempt
@login_required(login_url='login')
def get_order_status(request):
    order_id = request.session.get("order_id").replace('-', '')

    try:
        order = Order.objects.get(purchase_id=order_id)

        if order.paid:
            return JsonResponse({"status": "confirmed"})
        
        else:
            return JsonResponse({"status": "pending"})
        
    except Order.DoesNotExist:
        return JsonResponse({"status": "failed"})

@csrf_exempt
@login_required(login_url='login')
def payment_processing(request):
    return render(request, 'checkout/payment_processing.html')

@csrf_exempt
@login_required(login_url='login')
def payment_succeeded(request):
    order_id = request.session.get('order_id').replace('-', '')

    amount_paid = Order.objects.get(purchase_id=order_id)
    paid = round(float(amount_paid.amount), 2)

    context = {
        'order_id': order_id,
        'total': paid,
        'email': request.user.email,
    }


    return render(request, 'checkout/payment_succeeded.html', context=context)

@csrf_exempt
@login_required(login_url='login')
def payment_failed(request):
    return render(request, 'checkout/payment_failed.html')
