from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponse
from base.models import Clothing, Review, Order, OrderItem, ProductVariant, ClothingColor
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.models import User
from base.models import Order, OrderItem

import json
import requests
from django.db.models import Q
from django.contrib import messages


@login_required(login_url='login')
def user_profile(request):
    user = User.objects.get(username=request.user)

    try:
        reviews = Review.objects.filter(user_id=user.id)
        reviews = list(reviews)

    except Review.DoesNotExist:
        reviews = None

    context = {'user_profile': user,
               'reviews': reviews}


    if request.method == 'POST':
        first_name = request.POST.get('first_name') if request.POST.get('first_name') != "" else None
        last_name = request.POST.get('last_name') if request.POST.get('last_name') != "" else None
        email = request.POST.get('email') if request.POST.get('email') != "" else None

        if email:
            if '@' not in email or '.' not in email:
                messages.warning(request, 'invalid email address')
                return render(request, 'profile/user_profile.html', context)


        if request.POST.get('password1') != "" and request.POST.get('password2') != "":
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            if password1 != password2:
                messages.warning(request, 'invalid password - passwords must match')
                return render(request, 'profile/user_profile.html', context)
            
            else:
                user.password = password1

        if first_name != None:
            user.first_name = first_name

        if last_name != None:
            user.last_name = last_name

        if email != None:
            user.email = email

        user.save()

        return render(request, 'profile/user_profile.html', context)
    
    else:
        return render(request, 'profile/user_profile.html', context)

@login_required(login_url='login')
def activity(request):
    orders = []

    user_id = request.user.id

    orders_recent = Order.objects.filter(user_id_id=user_id)
    orders_recent = orders_recent[:4]

    print(orders_recent)

    for item in orders_recent:
        amount = item.amount
        paid = item.paid
        time = item.paid_time
        order_id = item.purchase_id


        orders.append([str(order_id), float(amount), paid, time])


    return render(request, 'profile/user_profile.html', context={'orders': orders})


"""
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
        return response.json()  # Parsed JSON response
    
    else:
        print("Error:", response.status_code, response.text)
        return None
"""


def order(request, pk):
    
    order_id = pk.replace('-', '')

    order = Order.objects.filter(purchase_id=order_id).exists()

    items = []

    if order == True:
        order = Order.objects.get(purchase_id=order_id)
        paid = order.paid

        order_items = OrderItem.objects.filter(purchase_id=order_id)

        for item in order_items:
            product_id = item.product_id_id

            variant_id = item.variant_id_id
            size = ProductVariant.objects.get(variant_id=variant_id).size

            name = Clothing.objects.get(product_id=item.product_id_id).name
            description = Clothing.objects.get(product_id=item.product_id_id).description

            quantity = item.quantity
            price = item.purchase_price

            color_id = ProductVariant.objects.get(variant_id=variant_id).color_id
            color = ClothingColor.objects.get(color_id=color_id).color

            items.append([product_id, description, size, name, color, quantity, price])

        order_details = requests.get(f'https://rest.sandbox.lalamove.com/v3/orders/{order_id}')
        print(order_details)

        order_details = order_details.json()

        print(order_details)

        if order_details["data"]["stops"][1]["POD"]["status"] == "DELIVERED":
            proof_link = order_details["data"]["stops"][1]["POD"]["image"]
            delivery_time = order_details["data"]["stops"][1]["POD"]["deliveredAt"]

            return render(request, 'profile/order.html', context={'items': items,
                                                                'order_id': order_id,
                                                                'order': order,
                                                                'tracker': None,
                                                                'proof_img': proof_link,
                                                                'time': delivery_time})

        else:
            shareLink = order_details["data"]["shareLink"]

            return render(request, 'profile/order.html', context={'items': items,
                                                                'order_id': order_id,
                                                                'order': order,
                                                                'tracker': shareLink})

    else:
        messages.error(request, 'Sorry, Order was not found')
        return redirect('home')