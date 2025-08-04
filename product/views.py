from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse
from base.forms import ReviewForm
from base.models import Review, User, Clothing, OrderItem, Order, ProductVariant, ClothingColor
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

def product(request, pk):
    pk = pk.replace('-', '')
    if request.method=='POST':
        color = request.POST.get('color')
        cart = request.session.get('cart', {})
        size = request.POST.get('size')

        print(color)
        print(size)

        if color != None:
            color = color.replace('-', '') if color != '' or color != None else None
        

        if color != None and size != '':
            key = pk + ':' + size + ';' + color
            stock = ProductVariant.objects.get(color_id=color, 
                                               product_id_id=pk, size=size).stock

        elif color == None and size != '':
            key = pk + ':' + size
            stock = ProductVariant.objects.get(product_id_id=pk, size=size).stock

        elif color != None and size == '':
            key = pk + ';' + color
            stock = ProductVariant.objects.get(product_id_id=pk, color_id=color).stock

        else:
            key = pk
            stock = ProductVariant.objects.get(product_id_id=pk).stock

        print(key)

        if Clothing.objects.filter(product_id=pk).exists():
            try:
                item = Clothing.objects.get(product_id=pk)

                if cart[key] < 20 and stock > cart[key] and stock > 4:
                    cart[key] += 1
                    request.session['cart'] = cart

                    messages.success(request, 'Added to cart')
                    return redirect('home')
                
                elif stock <= 4:
                    del cart[key]
                    messages.error(request, 'Item out of stock')
                    return redirect('home')

                elif stock < cart[key]:
                    cart[key] = stock - 4
                    return redirect('home')                     
                
                elif cart[key] >= 20:
                    messages.error(request, 'Maximum order number per item is 20')
                    return redirect('home')    

            except KeyError as e:
                cart[key] = 1
                request.session['cart'] = cart

                messages.success(request, 'Added to cart')
                return redirect('home')
    
    elif Clothing.objects.filter(product_id=pk).exists():
        pk = uuid.UUID(pk)

        product_variant = ProductVariant.objects.filter(product_id_id=pk)
        colors = ClothingColor.objects.filter(product_id_id=pk)

        variants = []
        colors = []
        sizes = []

        for item in product_variant:
            color_id = item.color_id
            size = item.size
            colorName = ClothingColor.objects.get(color_id=color_id).color

            variants.append([color_id, item.stock, item.size])            

            if not(any(colorName in row for row in colors)):
                colors.append([colorName, color_id])

            if not(any(size in row for row in sizes)):
                sizes.append(item.size)


        colors = None if colors[0][0] == None else colors

        variant_dicts = [{'color': c, 'stock': s, 'size': sz} for c, s, sz in variants]

        item = Clothing.objects.get(product_id=pk)

        description = item.description
        description = description.split(",")

        Reviews = Review.objects.filter(product_ID=pk)
        avg = 0
        count = 0

        try:
            for review in Reviews:
                avg = avg + review.stars
                count += 1

            avg = str(round((avg / count), 1))

        except ZeroDivisionError:
            Reviews = None

        try:
            user = User.objects.get(username=request.user)
            context = {
                "clothing": item,
                "reviews": Reviews,
                "description": description,
                "overall": avg,
                "curr_usr": user,
                "num_reviews": count,
                "variant_dicts": variant_dicts,
                "colors": colors,
                "sizes": sizes,
            }
            return render(request, "product/product.html", context)
        

        except User.DoesNotExist:
            context = {
                "clothing": item,
                "reviews": Reviews,
                "description": description,
                "overall": avg,
                "num_reviews": count,
                "variant_dicts": variant_dicts,
                "colors": colors,
                "sizes": sizes,
            }
            return render(request, "product/product.html", context)

    else:
        messages.error(request, 'Product does not exist')
        return redirect('home')

@login_required(login_url='login')
def create_review(request, pk):
    pk = pk.replace('-', '')
    # Checks if the review already exists (in that case, updates it)
    id = uuid.UUID(pk)
    if not Review.objects.filter(user_id=request.user, product_ID=id).exists():
        if request.method == 'POST':    # checks if submit button was pressed
            title = request.POST.get('title')
            reviewtext = request.POST.get('description_review')
            stars = int(request.POST.get('stars'))

            Prod = Clothing.objects.get(product_id=id)

            if filter.is_profane(title) or filter.is_profane(reviewtext):
                active=False

            else:
                active=True

            if OrderItem.objects.filter(product_id=Prod).exists() == True:
                verified=True

            else:
                verified=False

            new_item = Review(user_id=request.user,
                            description_review=reviewtext, 
                            is_active=active,
                            stars=stars,product_ID_id=id, 
                            verified=verified,title=title,)
                
                
            new_item.save()

            set_review(pk)
            return redirect('home')


        else:
            return render(request, "product/create_review.html", context={})

    else:
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

