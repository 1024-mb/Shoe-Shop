from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Clothing, User, Review
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .forms import SignUpForm, UpdateForm
from django.db.models import Q
from django.contrib import messages

def set_review(id_product):
    Reviews = Review.objects.filter(product_ID=id_product)
    avg = 0
    count = 0

    try:
        for Review in Reviews:
            avg = avg + Review.stars
            count += 1

        avg = str(round((avg / count), 1))

    except ZeroDivisionError:
        Reviews = None

    Product = Clothing.objects.get(product_id=id_product)
    Product.rating = avg
    Product.save()

def login_page(request):
    next_url = request.GET.get('next')

    if request.method == "POST":
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')

            UserChecked = User.objects.get(username__exact=username)

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
                userchecked = User.objects.get(username__exact=request.POST.get('username'))
                raise form.ValidationError('username is already in use')
            
            except User.DoesNotExist:
                user = form.save(commit=False)
                user.username = user.username
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
                    'child_categories': children_categories,
                    'order': order}

        return render(request, 'base/home.html', context)

@login_required(login_url='login')
def user_profile(request):
    update_detail = UpdateForm()
    user = User.objects.get(username=request.user)

    try:
        reviews = Review.objects.filter(user_id=user.id)
        reviews = list(reviews)

    except Review.DoesNotExist:
        reviews = None

    context = {'user_profile': user,
        'update_detail': update_detail,
        'reviews': reviews}


    if request.method == 'POST':
        first_name = request.POST.get('first_name') if request.POST.get('first_name') != "" else None
        last_name = request.POST.get('last_name') if request.POST.get('last_name') != "" else None
        email = request.POST.get('email') if request.POST.get('email') != "" else None

        if email:
            if '@' not in email or '.' not in email:
                messages.warning(request, 'invalid email address')
                return render(request, 'user_profile.html', context)


        if request.POST.get('password1') != "" and request.POST.get('password2') != "":
            print(request.POST.get('password1'))
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            if password1 != password2:
                messages.warning(request, 'invalid password - passwords must match')
                return render(request, 'user_profile.html', context)
            
            else:
                user.password = password1

        if first_name != None:
            user.first_name = first_name

        if last_name != None:
            user.last_name = last_name

        if email != None:
            user.email = email

        user.save()

        return render(request, 'user_profile.html', context)
    
    else:
        return render(request, 'user_profile.html', context)
    
@login_required(login_url='login')
def Logout(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('home')

    else:
        return redirect('home')


