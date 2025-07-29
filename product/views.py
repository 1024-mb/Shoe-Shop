from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse
from base.forms import ReviewForm
from base.models import Review, User, Clothing, Order
import uuid
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from base.views import set_review

from glin_profanity import Filter

filter = Filter()

"""
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    request.session.modified = True

"""

# Create your views here.
def product(request, pk):
    from base.models import Clothing
    from base.models import Review

    product = None

    products = Clothing.objects.order_by('-updated', '-created')

    for item in products:
        id_product = item.product_id
        cmp = str(item.product_id)

        if cmp == pk:
            product = item

            description = item.description
            description = description.split(",")

            product.description = description

            sizes = item.size
            sizes = sizes.split(",")

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

            try:
                user = User.objects.get(username=request.user)
                context = {
                "clothing": product,
                "reviews": Reviews,
                "overall": avg,
                "curr_usr": user,
                "num_reviews": count,
                "sizes": sizes,
                }

                return render(request, "product/product.html", context)

            except User.DoesNotExist:
                context = {
                "clothing": product,
                "reviews": Reviews,
                "overall": avg,
                "num_reviews": count,
                "sizes": sizes,
                }

                return render(request, "product/product.html", context)
 
    return HttpResponse("404 page not found ")

@login_required(login_url='login')
def create_review(request, pk):
    pk = uuid.UUID(pk)

    # Checks if the review already exists (in that case, updates it)
    if not Review.objects.filter(user_id=request.user, product_ID=pk).exists():

        if request.method == 'POST':    # checks if submit button was pressed
            title = request.POST.get('title')
            reviewtext = request.POST.get('description_review')
            stars = int(request.POST.get('stars'))

            id = uuid.UUID(pk)
            Prod = Clothing.objects.get(product_id=id)

            if filter.is_profane(title) or filter.is_profane(reviewtext):
                active=False

            else:
                active=True

            if Order.objects.get(user_id=request.user, product_ID=Prod).exists() == True:
                verified=True

            else:
                verified=False

            new_item = Review(user_id=request.user,
                            description_review=reviewtext, 
                            stars=stars,product_ID_id=pk, 
                            verified=verified,title=title,)
                
                
            new_item.save()

            set_review(pk)
            return redirect('home')


        else:
            return render(request, "product/create_review.html", context={})

    else:
        pk = str(pk)
        return redirect(f'http://127.0.0.1:8000/product/{pk}/update_review')

@login_required(login_url='login')
def update_review(request, pk):
    queryreview = uuid.UUID(pk)

    curr_user = User.objects.get(username=request.user)
    usr = curr_user.id
    review = Review.objects.get(product_ID=queryreview, user_id=usr)

    curr_title = review.title
    curr_desc = review.description_review
    curr_stars = review.stars

    try:

        if request.method == 'POST':         
            url_add = str(pk)

            new_title = request.POST.get('title') if request.POST.get('title') != '' else None
            new_desc = request.POST.get('description_review') if request.POST.get('description_review') != '' else None
            new_stars = request.POST.get('stars') if request.POST.get('stars') != '' else None

            id = uuid.UUID(pk)
            Prod = Clothing.objects.get(product_id=id)

            if filter.is_profane(new_title) or filter.is_profane(new_desc):
                review.is_active = False

            else:
                review.is_active = True

            if new_title:
                review.title = new_title

            if new_desc:
                review.description_review = new_desc

            if new_stars:
                review.stars = new_stars


            review.save()

            set_review(pk)
            return redirect(f'http://127.0.0.1:8000/product/{ url_add }')
            
    except:
        return redirect('home')

    return render(request, 'product/create_review.html', context={'curr_title': curr_title,
                                                                  'curr_desc': curr_desc,
                                                                  'curr_stars': curr_stars,})


@login_required(login_url='login')
def delete_review(request, pk):
    queryreview = uuid.UUID(pk)
    url_add = str(pk)
    
    curr_user = User.objects.get(username=request.user)
    usr = curr_user.id

    review = Review.objects.get(product_ID=queryreview, user_id=usr)

    if request.method == 'POST':
        review.delete()
        set_review(pk)
        
        return redirect(f'http://127.0.0.1:8000/product/{url_add}')

    else:
        context = {'review':review}

        return render(request, 'product/delete_review.html', context)

@login_required(login_url='login')
def add_to_cart(request, pk):
    cart = request.session.get('cart', {})
    if Clothing.objects.filter(product_id=pk).exists():
        try:
            cart[pk] += 1
            request.session['cart'] = cart

        except KeyError as e:
            cart[pk] = 1
            request.session['cart'] = cart

    messages.success(request, 'Added to cart')
    return redirect('home')

