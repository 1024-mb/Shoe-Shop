from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from base.models import Clothing

@login_required(login_url='login')
def cart(request):
    cart = request.session.get('cart', {})

    if request.method == 'POST':
        total = 0
        for item in cart:
            quantity = request.POST.get(f'{item}')
            NewItem = Clothing.objects.get(product_id=item)
            
            total += (NewItem.price * quantity)
            
            request.session['total'] = total
            (request.session['cart'])[item] = quantity

        context = {'total': total}
        return redirect('checkout')

    else:
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
