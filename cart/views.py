from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from base.models import Clothing
from django.contrib import messages

@login_required(login_url='login')
def cart(request):
    cart = request.session.get('cart', {})

    if request.method == 'POST':
        total = 0
        for item in cart:  
            quantity = request.POST.get(f'{item}') if request.POST.get(f'{item}') != None else 0
            quantity = int(quantity)

            NewItem = Clothing.objects.get(product_id=item)
            
            price = float(NewItem.price)

            total += (price * quantity)
            
            
            (request.session['cart'])[item] = quantity

        request.session['total'] = float(total)

        context = {'total': total}
        return redirect('checkout')

    else:
        products = []
        total = 0

        for item in cart:
            NewItem = Clothing.objects.get(product_id=item)
            products.append([NewItem, int(cart[item])])

            total += NewItem.price * cart[item]

        total = round(total, 2)
        request.session['total'] = float(total)

        context = {'products': products,
                   'cart': request.session.get('cart', {}),
                   'total': total}

        return render(request, 'cart/cart.html', context)


@login_required(login_url='login')
def clear_cart(request):
    request.session['cart'] = {}
    
    messages.success(request, 'Cart cleared successfully')
    return redirect('home')


# Create your views here.
