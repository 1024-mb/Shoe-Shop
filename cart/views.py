from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from base.models import Clothing, Order, OrderItem, User
from django.contrib import messages
import uuid

@login_required(login_url='login')
def cart(request):
    cart = request.session.get('cart', {})

    if request.method == 'POST':
        total = 0
        for item in cart:
            pos_id = item.index(':')
            id = item[:pos_id]            
            quantity = float(request.POST.get(f'{id}')) if request.POST.get(f'{id}') != None else 0


            NewItem = Clothing.objects.get(product_id=id)
            price = float(NewItem.price)
            print(price)

            total += (price * quantity)

        request.session['total'] = float(total)

        create_order = Order(amount=total, paid=False, 
                             user_id_id=request.user.id,)
        create_order.save()

        for item in cart:
            pos_id = item.index(':')
            id = item[:pos_id]
            NewItem = Clothing.objects.get(product_id=id)
            
            price = float(NewItem.price)

            order_item = OrderItem(purchase=create_order,
                                   product_id=NewItem, 
                                   quantity=int(cart[item]),
                                   purchase_price=price,)
            
            order_item.save()

        request.session['order_id'] = str(create_order.purchase_id)

        
        print(request.session['order_id'])

        return redirect('checkout')

    else:
        products = []
        total = 0

        for item in cart:
            position_size = item.index(":")
            size=item[(position_size+1):]
            id = item[:position_size]

            NewItem = Clothing.objects.get(product_id=id)
            quantity = int(cart[item])

            products.append([NewItem, quantity, NewItem.stock, size])

            price = float(NewItem.price)
            total += (price * quantity)

        total = round(total, 2)
        request.session['total'] = total

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
