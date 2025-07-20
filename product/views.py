from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse
from base.forms import ReviewForm
from base.models import Review

# Create your views here.
def product(request, pk):
    from base.models import Clothing
    from base.models import Review

    product = None

    Products = Clothing.objects.order_by('-updated', '-created')

    for item in Products:
        id_product = item.product_id
        cmp = str(item.product_id)

        if cmp == pk:
            product = item

            description = item.desc
            description = description.split(",")

            product.desc = description

            sizes = item.size
            sizes = sizes.split(",")

            product.size = sizes

            context = {'clothing': product}


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

            context = {
                "clothing": product,
                "reviews": Reviews,
                "overall": avg
            }



            return render(request, "product/product.html", context)


    return HttpResponse("404 page not found ")

def create_review(request, pk):
    form = ReviewForm()

    if request.method == 'POST':    # checks if submit button was pressed

        form = ReviewForm(request.POST)


        if form.is_valid():
            form.save()     # saves the form contents to the database

        return redirect(request, 'http://127.0.0.1:8000')

    context = {'form': form}

    return render(request, "product_review.html", context)


def update_review(request, pk):
    review = Review.objects.get(review_id=pk)
    form = ReviewForm(instance=review)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        
        url_add = request.POST.get('product_id')
        if form.is_valid():
            form.save()
            return redirect(request, 'http://127.0.0.1:8000')


    context = {'form': form}

    return render(request, 'base/room_form.html', context)
