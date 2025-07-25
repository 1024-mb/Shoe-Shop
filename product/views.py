from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse
from base.forms import ReviewForm
from base.models import Review, User
import uuid
from django.contrib.auth.decorators import login_required

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
            print(sizes)



            Reviews = Review.objects.filter(product_ID=id_product)
            avg = 0
            count = 0

            try:
                for Review in Reviews:

                    avg = avg + Review.stars
                    count += 1

                avg = str(avg / count)

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
    if not Review.objects.filter(user_id=request.user, product_ID=pk).exists():

        if request.method == 'POST':    # checks if submit button was pressed

            form = ReviewForm(request.POST)

            if form.is_valid():
                reviewtext = request.POST.get('description_review')
                stars = request.POST.get('stars')

                new_item = Review(description_review=reviewtext, 
                                  stars=stars, product_ID_id=pk, user_id=request.user)     # saves the form contents to the database
                new_item.save()

            return redirect('home')

        form = ReviewForm()
        context = {'form': form}

        return render(request, "product_review.html", context)

    else:
        pk = str(pk)
        return redirect(f'http://127.0.0.1:8000/product/{pk}/update_review')

@login_required(login_url='login')
def update_review(request, pk):
    queryreview = uuid.UUID(pk)


    try:
        curr_user = User.objects.get(username=request.user)
        usr = curr_user.id

        review = Review.objects.get(product_ID=queryreview, user_id=usr)
        form = ReviewForm(instance=review)

        if request.method == 'POST':
            form = ReviewForm(request.POST, instance=review)
            
            url_add = str(pk)
            if form.is_valid():
                form.save()
                return redirect(f'http://127.0.0.1:8000/product/{ url_add }')
            
    except:
        return redirect('home')


    context = {'form': form}

    return render(request, 'product_review.html', context)

@login_required(login_url='login')
def delete_review(request, pk):
    queryreview = uuid.UUID(pk)
    url_add = str(pk)
    
    curr_user = User.objects.get(username=request.user)
    usr = curr_user.id

    review = Review.objects.get(product_ID=queryreview, user_id=usr)

    if request.method == 'POST':
        review.delete()

        return redirect(f'http://127.0.0.1:8000/product/{ url_add }')

    else:
        context = {'review':review}


        return render(request, 'delete_review.html', context)

