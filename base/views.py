from django.shortcuts import render
from django.http import HttpResponse
from .models import Clothing, User
from django.db.models import Q
from django.contrib import messages

# Create your views here.
def home(request):
    if request.method =='POST':
        print("Hi")
    
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
    
def login_page(request):
    
    if request.method == "POST":
        if form.is_valid() == True:
            try:
                username = request.GET.get('username')
                password = request.GET.get('password')

                UserChecked = User.objects.get(username=username)

            except:
                messages.warning(request, "Incorrect Username/Password")

                context = {'operation': 'login'}
                return render(request, 'login_register.html', context)
    else:
        context = {'operation': 'login'}
        return render(request, 'login_register.html', context)
    


def logout(request):
    if request.method == "POST":
        pass

    else:
        context = {'operation': 'logout'}
        return render(request, 'login_register.html', context)
    
