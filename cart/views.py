from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from base.models import Clothing

@login_required(login_url='login')
def cart(request):
    cart = request.session.get('cart', {})
    products = []

    total = 0

    for item in cart:
        NewItem = Clothing.objects.get(product_id=item)
        products.append([NewItem, cart[item]])

        total += NewItem.price

    total = round(total, 2)

    context = {'products': products,
               'cart': request.session.get('cart', {}),
               'total': total}

    return render(request, 'cart/cart.html', context)


# Create your views here.
