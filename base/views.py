from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Clothing, User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.contrib import messages


def login_page(request):
    next_url = request.GET.get('next')

    if request.method == "POST":
        try:
            username = request.POST.get('username')
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
    signup_form = UserCreationForm()
    if request.method == "POST":
        username = request.GET.get('username')
        password = request.GET.get('password')
        email = request.GET.get('email')
        firstname = request.GET.get('firstname')
        firstname = request.GET.get('lastname')

        try:
            userchecked = User.objects.get(username=username)
        
        except User.DoesNotExist:
            pass


    else:
        context = {'operation': 'Signup'}
        return render(request, 'login_register.html', context)

# Create your views here.
def home(request):
    q = request.GET.get('q')

    if q != None:
        all_categories = Clothing.objects.order_by('-rating')
        extracted = Clothing.objects.filter(
            Q(category__icontains=q) |
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(category__icontains=q) |
            Q(brand__icontains=q)).order_by('-rating')


        context = {'clothing': extracted,
                   'categories': all_categories,
                   'query': q,
                   'result_count': extracted.count()}


        return render(request, 'base/home.html', context)
    
    else:
        extracted = Clothing.objects.order_by('-rating')

        context = {'clothing': extracted,
                   'categories': extracted}

        return render(request, 'base/home.html', context)

@login_required(login_url='login')
def Logout(request):
    logout(request)
    return redirect('home')

