from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Clothing, User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .forms import SignUpForm
from django.db.models import Q
from django.contrib import messages


def login_page(request):
    next_url = request.GET.get('next')

    if request.method == "POST":
        try:
            username = request.POST.get('username').lower()
            password = request.POST.get('password')

            UserChecked = User.objects.get(username=username)

            user = authenticate(request, username=username, password=password)

            try:
                login(request, user)

                if next_url:
                    return redirect(next_url)
                
                else:
                    return redirect('home')

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

def register(request):
    signup_form = SignUpForm()

    if request.method == "POST":
        form = SignUpForm(request.POST)
        
        if form.is_valid():
            if '@' not in request.POST.get('email'):
                raise form.ValidationError('email is invalid')
            
            if len(request.POST.get('username')) > 150:
                raise form.ValidationError('username is too long')
            

            try:
                userchecked = User.objects.get(username=request.POST.get('username'))
                raise form.ValidationError('username is already in use')
            
            except User.DoesNotExist:
                user = form.save(commit=False)
                user.username = user.username.lower()
                user.save()

                login(request, user)
                messages.success(request, 'Account created')

                return redirect('home')

        else:
            if '@' not in request.POST.get('email'):
                messages.error(request, 'Please enter a valid email address')
                context = {'operation': 'Signup',
                        'form': signup_form}
                
                return render(request, 'login_register.html', context)
            
            if len(request.POST.get('username')) > 150:
                messages.error(request, 'Username is greater than 150 characters')

                context = {'operation': 'Signup',
                        'form': signup_form}
                
                return render(request, 'login_register.html', context)
            
            try:
                userchecked = User.objects.get(username=request.POST.get('username'))
                messages.error(request, 'Username is already taken')
                
                context = {'operation': 'Signup',
                        'form': signup_form}
                
                return render(request, 'login_register.html', context)
            
            except:
                pass

            context = {'operation': 'Signup',
                    'form': signup_form}
            
            return render(request, 'login_register.html', context)


    else:
        context = {'operation': 'Signup',
                   'form': signup_form}
        
        return render(request, 'login_register.html', context)

# Create your views here.
def home(request):
    order = '-rating'
    if request.method == 'POST':
        order = request.POST.get('order')
        print(order)
        
        if order == 'new_to_old':
            order = '-created'
            print('126')

        elif order == 'old_to_new':
            order = 'created'
            print('130')        

        elif order == 'low_to_high':
            order = 'price'
            print('134')

        elif order == 'high_to_low':
            order = '-price'
            print('138')

        elif order == 'top_rated':
            order = '-rating'
            print('142')

    q = request.GET.get('q')

    men_categories = ['T-Shirts & Tops', 'Jerseys', 'Hoodies',
                    'Sweatshirts and Tracksuits', 'Pants', 'Tights', 'Shorts',
                    'Sportswear']
    
    women_categories = ['T-Shirts & Tops', 'Jerseys', 'Hoodies',
                        'Sweatshirts and Tracksuits', 'Sports Bras', 'Jerseys',
                        'Hoodies', 'Jackets', 'Pants', 'Tights', 'Shorts',
                        'Sportswear',]
    
    children_categories = ['New Arrivals', 'Boys Clothing', 'Girls Clothing',
                            'Boys Shoes', 'Girls Shoes']

    if q != None:
        extracted = Clothing.objects.filter(
            Q(category__icontains=q) |
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(category__icontains=q) |
            Q(brand__icontains=q)).order_by(order)


        context = {'clothing': extracted,
                   'mens_categories': men_categories,
                   'womens_categories': women_categories,
                   'child_categories': children_categories,
                   'query': q,
                   'result_count': extracted.count()}


        return render(request, 'base/home.html', context)
    
    else:
        extracted = Clothing.objects.order_by(order)

        context = {'clothing': extracted,
                    'mens_categories': men_categories,
                    'womens_categories': women_categories,
                    'child_categories': children_categories}

        return render(request, 'base/home.html', context)

@login_required(login_url='login')
def Logout(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('home')

    else:
        return redirect('home')

