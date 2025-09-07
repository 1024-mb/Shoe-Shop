from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Clothing, Review, Order, OrderItem, ProductVariant
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from email.message import EmailMessage

from datetime import datetime

from datetime import datetime

from django.contrib.auth.models import User

from django.forms import ValidationError
from .forms import SignUpForm, UpdateForm
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.sessions.models import Session

from email.message import EmailMessage

import random
import json

import stripe
import os
import uuid
import smtplib

import random

stripe.api_key = os.getenv('stripekey')

def send_otp(first_name, otp, usr_email, subject):
    receipt = EmailMessage()
    receipt['Subject'] = subject
    receipt['From'] = 'm.sajjad.2007.jan@gmail.com'
    receipt['To'] = usr_email
    
    receipt.set_content('Email follows')

    emailText = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <style>
        
        </style>
    </head>

    <body>
        <h2>{subject}</h2>
        <p>Dear Valued Customer,
        Your OTP is: {otp}. This OTP is valid
        for 15 minutes. If you did not request an OTP, please ignore this email.
        
        </p>
    </body>

    </html>

    """

    receipt.add_alternative(emailText, subtype='html')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('m.sajjad.2007.jan@gmail.com', 'yufr nluw qvwy jaid')
        smtp.send_message(receipt)

def set_review(id_product):
    Reviews = Review.objects.filter(product_ID=id_product)
    avg = 0
    count = 0

    try:
        for review in Reviews:
            avg = avg + review.stars
            count += 1

        avg = str(round((avg / count), 1))

    except ZeroDivisionError:
        Reviews = None

    Product = Clothing.objects.get(product_id=id_product)
    Product.rating = avg
    Product.save()

def login_page(request):
    if not(request.user.is_authenticated):
        next_url = request.GET.get('next')

        if request.method == "POST":
            try:
                username = request.POST.get('username')
                password = request.POST.get('password')

                UserChecked = User.objects.get(username__exact=username)

                user = authenticate(request, username=username, password=password)

                try:
                    if UserChecked.is_active == True:
                        login(request, user)

                        if next_url:
                            return redirect(next_url)
                        
                        else:
                            return redirect('home')
                        
                    else:
                        request.session['user_id'] = UserChecked.id
                        request.session['first_name'] = UserChecked.first_name
                        request.session['email'] = UserChecked.email

                        messages.error(request, 'Account setup not fully completed.')
                        return redirect('confirm_email')

                except AttributeError:
                    messages.warning(request, "Password is incorrect")
                    
                    context = {'operation': 'login'}
                    return render(request, 'login_register.html', context)
                
            except User.DoesNotExist:
                messages.warning(request, "User does not exist")
                context = {'operation': 'login'}
                return render(request, 'login_register.html', context)
                

        else:
            context = {'operation': 'login'}
            return render(request, 'login_register.html', context)
        
    else:
        messages.error(request, 'Already signed in')
        return redirect('home')

def confirm_email(request):
    if int(request.session.get('count', 0)) < 7 and not(request.user.is_authenticated):
        if request.method == 'POST':
            if request.POST.get('OTP') != '' and (datetime.now() - datetime.strptime(request.session['time'],  '%Y-%m-%d %H:%M:%S.%f')).total_seconds() < 900:
                datetime_object = datetime.strptime(request.session['time'],  '%Y-%m-%d %H:%M:%S.%f')
                time_elapsed = datetime.now() - datetime_object

                user_input = str(request.POST.get('OTP'))
                stored_otp = str(request.session.get('otp'))

                if user_input == stored_otp:
                    account = User.objects.get(id=request.session.get('user_id'))

                    account.is_active = True
                    account.save()

                    return redirect('login')

                else:
                    user_created = request.session.get('user_id')
                    messages.error(request, 'Incorrect OTP entered')

                    request.session['count'] = int(request.session.get('count', 0)) + 1

                    return redirect('confirm_email')

            elif (datetime.now() - datetime.strptime(request.session['time'],  '%Y-%m-%d %H:%M:%S.%f')).total_seconds() > 900:
                messages.error(request, 'The OTP has expired')
                return redirect('confirm_email')

            else:
                otp = str(random.randint(100000, 999999))  # 6-digit OTP

                # send_otp(first_name, otp, usr_email)
                send_otp(request.session.get('first_name'), otp, request.session.get('email'), 'HeatSneakers | Confirm Account')

                time = str(datetime.now())
                request.session['time'] = time


                # Optionally store OTP in session or database for verification
                request.session['otp'] = str(otp)
                request.session['count'] = int(request.session.get('count', 0)) + 1

                return redirect('confirm_email')

        else:
            otp = str(random.randint(100000, 999999))  # 6-digit OTP

            send_otp(request.session.get('first_name'), otp, request.session.get('email'), 'HeatSneakers | Confirm Account')

            time = str(datetime.now())
            request.session['time'] = time

            # Optionally store OTP in session or database for verification
            request.session['otp'] = otp
            
            return render(request, 'confirm_email.html', context={})

    elif request.user.is_authenticated:
        messages.error(request, 'Error: user already authenticated')
        return redirect('home')

    else:
        user_created = request.session.get('user_id')

        user_obj = User.objects.get(id=user_created)
        user_obj.delete()

        messages.error(request, 'Too many unsuccessful attempts.')
        return redirect('home')

def set_password(request):
    if request.method == "POST" and request.POST.get('password1') != '':
        try:
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            usr_email = request.session.get('email')
            username = request.session.get('username')

            ChangePassword = User.objects.get(email=usr_email, username=username)


            if password1 == password2:
                ChangePassword.set_password(password1)
                ChangePassword.save()

            else:
                messages.error(request, 'Passwords much match')
                return render(request, 'set_password.html', context={})


            messages.success(request, 'Password changed successfully')
            return redirect('login')

            
        except User.DoesNotExist:
            messages.error(request, 'User does not exist')
            return redirect('login')

    else:
        return render(request, 'set_password.html', context={})

def enter_code(request):
    if request.method == 'POST' and request.session.get('sentTime', None) != None and request.POST.get('resendBtn') != 'resendOTP':
        code = str(request.POST.get('OTP'))
        otp = str(request.session.get('OTP', None))
        timeStart = datetime.strptime(request.session.get('sentTime', None),  '%Y-%m-%d %H:%M:%S.%f')
        timeElapsed = datetime.now() - timeStart

        email = request.session.get('email', None)

        UserChecked = User.objects.filter(email__exact=email)
        print(UserChecked)

        if email and code == otp and UserChecked.exists() and timeElapsed.total_seconds() < 900:
            return redirect('set_password')
        
        elif timeElapsed.total_seconds() > 900:
            messages.error(request, 'Your session timed out. Please try again')
            return redirect('reset_password')

        else:
            return redirect('login')

    elif request.POST.get('resendBtn') == 'resendOTP':
        otp = random.randint(100000, 999999)
        request.session['OTP'] = otp

        send_otp(request.session.get('first_name'), otp, request.session.get('email'), 'HeatSneakers | Reset Password')

        return redirect('enter_code')

    else:
        return render(request, 'enter_code.html')

def reset_password(request):
    if request.method == 'POST':
        usr_email = request.POST.get('email')
        username = request.POST.get('username')
        userAssociated = User.objects.filter(email=usr_email, username=username)

        if userAssociated.exists():
            otp = random.randint(100000, 999999)
            request.session['OTP'] = otp
            request.session['email'] = usr_email
            request.session['username'] = username
            request.session['sentTime'] = str(datetime.now())

            first_name = userAssociated[0].first_name

            send_otp(first_name, otp, usr_email, 'HeatSneakers | Reset Password')

            return redirect('enter_code')
        
        else:
            messages.error(request, "Account associated with this email doesn't exist")
            return redirect('login')

    else:
        return render(request, 'reset_password.html')

def register(request):
    if request.method == "POST":
        if '@' not in request.POST.get('email'):
            context = {'operation': 'Signup',
                       'error': 'Error: invalid e-mail'}

            return render(request, 'login_register.html', context)
            
            
        
        if len(request.POST.get('username')) > 150:
            context = {'operation': 'Signup',
                       'error': 'Username must be less than 150 characters'}

            return render(request, 'login_register.html', context)
        

        if request.POST.get('password1') != request.POST.get('password2'):
            context = {'operation': 'Signup',
                       'error': 'Passwords do not match'}

            return render(request, 'login_register.html', context)

        if User.objects.filter(username=request.POST.get('username')).exists() == True:
            context = {'operation': 'Signup',
                       'error': 'Username already in use'}

            return render(request, 'login_register.html', context)

        else:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password1')

            user = User(username=username, email=email, last_name=last_name, first_name=first_name)
            user.set_password(password)

            user.is_active = False
            user.save()

            messages.success(request, 'Account created!')

            request.session['user_id'] = user.id
            request.session['email'] = email
            request.session['first_name'] = first_name
            request.session['username'] = username

            return redirect('confirm_email')


    else:
        context = {'operation': 'Signup'}
        return render(request, 'login_register.html', context)

# Create your views here.
def home(request):
    order = '-rating'
    if request.method == 'POST':
        order = request.POST.get('order')
        
        if order == 'new_to_old':
            order = '-created'

        elif order == 'old_to_new':
            order = 'created'

        elif order == 'low_to_high':
            order = 'price'

        elif order == 'high_to_low':
            order = '-price'

        elif order == 'top_rated':
            order = '-rating'

    q = request.GET.get('q').replace('%20', ' ') if request.GET.get('q') != None else None

    all_categories = ['T-Shirts & Tops', 'Jerseys', 'Hoodies',
                      'Sweatshirts and Tracksuits', 'Shorts']

    men_categories = ['Pants', 'Tights',
                      'Sportswear']
    
    women_categories = ['Sports Bras', 'Jackets', 'Pants', 'Tights', 
                        'Sportswear']
    
    children_categories = ['Boys Clothing', 'Girls Clothing',
                            'Boys Shoes', 'Girls Shoes']

    if q != None:
        extracted = Clothing.objects.filter(
            Q(category__icontains=q) |
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(category__icontains=q) |
            Q(brand__icontains=q)).order_by(order)

        context = {'clothing': extracted,
                   'all_categories': all_categories,
                   'mens_categories': men_categories,
                   'womens_categories': women_categories,
                   'child_categories': children_categories,
                   'query': q,
                   'result_count': extracted.count(),
                    'order': order}


        return render(request, 'base/home.html', context)
    
    else:
        extracted = Clothing.objects.order_by(order)

        context = {'clothing': extracted,
                   'all_categories': all_categories,
                    'mens_categories': men_categories,
                    'womens_categories': women_categories,
                    'query': None,
                    'child_categories': children_categories,
                    'order': order}

        return render(request, 'base/home.html', context)

@login_required(login_url='login')
def logout_page(request):
    if request.user.is_authenticated:
        messages.success(request, 'Logged out')
        logout(request)
        return redirect('home')

    else:
        return redirect('home')

@csrf_exempt
def stripe_webhook(request):
    total = 0
    payload = request.body

    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = 'whsec_1709d3d9f617576b171944a41c57eb6ba8e8ac16682a96593015280d92de2763'
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception as e:
        print(f"Webhook error: {e}")
        return HttpResponse(status=400)

    intent = event['data']['object']
    order_id = intent['metadata'].get('order_id')

    order_return = Order.objects.get(purchase_id=order_id)
    
    print('299')

    if event['type'] == 'charge.succeeded':
        request.session['cart'] = {}
        request.session['order_id'] = ''
        print(request.session['cart'])

        print('241')

        order_return.paid = True
        paid_time = datetime.now()
        order_return.paid_time = paid_time.strftime("%Y-%m-%d %H:%M:%S")

        order_return.save()
        items = OrderItem.objects.filter(purchase_id=order_id)

        receipt_items = []

        for item in items:
            quantity = item.quantity
            product = ProductVariant.objects.get(variant_id=item.variant_id_id)
            productPrice = Clothing.objects.get(product_id=product.product_id_id)

            product.stock -= quantity
            product.save()

            price = round(float(quantity * productPrice.price), 2)
            total += round(price, 2)

            receipt_items.append([productPrice, quantity, price])


        userID = order_return.user_id_id
        user = User.objects.get(id=userID)
        emailAddress = user.email
        name = user.first_name

        receipt = EmailMessage()
        receipt['Subject'] = 'HeatSneakers | Receipt of purchase'
        receipt['From'] = 'm.sajjad.2007.jan@gmail.com'
        receipt['To'] = emailAddress

        receipt.set_content('Email follows')


        first_component = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <style>
                h2 {
                    color: #E31E27;
                }

                body {
                    font-family: sans-serif;
                }

                a {
                    color: #E31E27;
                }

                th {
                    padding: 15px;
                }

                thead {
                    padding: 10px;
                    outline: 1px solid black
                }

                table {
                    outline: none;
                    border: none;
                }
            </style>
        </head>
        """ + f"""
        <body>
            <h2>Order ID: { order_id }</h2>
            <p>Dear {name.capitalize()},
               This is the receipt for your recent purchase on our website.
               We hope you are satisfied with your purchase and our service.
               Should you have any queries, please don't hesitate to 
               <a href="mailto:m.sajjad.2007.jan@gmail.com"> reach out</a>
            
            </p>

            <table border="1">
            <thead>
                <tr>
                    <th>Category</th>
                    <th>Item Name</th>
                    <th>Quantity</th>
                    <th>Total Price</th>
                </tr>
            </thead>
            <tbody>
        """

        for item, quantity, price in receipt_items:
            if quantity > 0:
                price = round(price, 2)
                first_component += f"""
                <tr>
                    <td>{item.category}</td>
                    <td>{item.name}</td>
                    <td>{quantity}</td>
                    <td>MYR {price:.2f}</td>
                </tr>
                """

        total = round(total, 2)
        first_component += f"""
            </tbody>
            </table>

            <hr>
            Total amount: MYR {total:.2f}
            <hr>

            <p>Thank you for shopping with HeatSneakers. We wish you all
               the best and hope our services are to your standards.
               Please do not heistate 
               <a href="mailto:m.sajjad.2007.jan@gmail.com">to submit feedback.</a>
               Your feedback is of immense value to our services

            </p>

            
        </body>
        </html>
        """

        receipt.add_alternative(first_component, subtype='html')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login('m.sajjad.2007.jan@gmail.com', 'yufr nluw qvwy jaid')
            smtp.send_message(receipt)


    elif event['type'] == 'payment_intent.payment_failed':
        order_return.paid = False
        order_return.save()

    elif event['type'] == 'payment_intent.canceled':
        order_return.paid = False
        order_return.save()

    elif event['type'] == 'payment_intent.processing':
        order_return.paid = False
        order_return.save()

    elif event['type'] == 'payment_intent.confirmed':
        order_return.paid = False
        order_return.save()

        
    try:
        print('here')
        order_return.save()
        return HttpResponse(status=200)

    except Exception as e:
        print(e + 'line 421 views.py base')
        return HttpResponse(status=500)
