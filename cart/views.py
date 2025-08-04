from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from base.models import Clothing, Order, OrderItem, User, ProductVariant, ClothingColor
from django.contrib import messages
import uuid

@login_required(login_url='login')
def cart(request):
    cart = request.session.get('cart', {})

    if request.method == 'POST':
        total = 0

        for item in cart:
            id = item[:32]

            product = Clothing.objects.get(product_id=id)
            price = float(product.price)

            quantity = float(request.POST.get(f'{item}')) if request.POST.get(f'{item}') != None else 0

            total += (price * quantity)

        create_order = Order(amount=total, paid=False, 
                        user_id_id=request.user.id,)
        
        create_order.save()


        for item in cart:
            id = item[:32]

            if ':' in item and ';' in item:
                pos_id = item.index(':')
                id = item[:pos_id]

                pos_size = item.index(';')
                size = item[pos_id+1:pos_size]

                color = item[pos_size+1:]

                stockItem = ProductVariant.objects.get(size=size, color_id=color, product_id_id=id)

            elif ':' in item:
                pos_id = item.index(':')
                id = item[:pos_id]

                size = item[pos_id+1:]

                stockItem = ProductVariant.objects.get(size=size, product_id_id=id)


            elif ';' in item:
                pos_color = item.index(';')
                color = item[pos_color+1:]
                
                id = item[:pos_color]

                stockItem = ProductVariant.objects.get(color_id=color, product_id_id=id)



            NewItem = Clothing.objects.get(product_id=id)
            
            price = float(NewItem.price)

            quantity = float(request.POST.get(f'{item}')) if request.POST.get(f'{item}') != None else 0

            order_item = OrderItem(purchase_id=create_order.purchase_id,
                                   product_id_id=id.replace('-', ''),
                                   user_id_id=request.user.id,
                                   quantity=int(quantity),
                                   purchase_price=price,
                                   variant_id_id=stockItem.variant_id)
            
            order_item.save()
            

        request.session['total'] = float(total)
        request.session['order_id'] = str(create_order.purchase_id)

        return redirect('checkout')

    else:
        products = []
        total = 0

        for item in cart:
            # 59c559f5-37fd-489d-aae1-453cecd9d335:29;59c559f5-37fd-489d-aae1-453cecd9d335

            print(item)
            item = item.replace('-', '')
            if ':' in item and ';' in item:
                pos_id = item.index(':')
                id = item[:pos_id]

                pos_size = item.index(';')
                size = item[pos_id+1:pos_size]

                color = item[pos_size+1:]

                stockItem = ProductVariant.objects.get(size=size, color_id=color, product_id_id=id)

            elif ':' in item:
                pos_id = item.index(':')
                id = item[:pos_id]

                size = item[pos_id+1:]

                stockItem = ProductVariant.objects.get(size=size, product_id_id=id)


            elif ';' in item:
                pos_color = item.index(';')
                color = item[pos_color+1:]
                
                id = item[:pos_color]

                stockItem = ProductVariant.objects.get(color_id=color, product_id_id=id)

            else:
                stockItem = ProductVariant.objects.get(product_id_id=id)


            # {% for item, qty, stock, size in products %}

            stock = stockItem.stock
            quantity = cart[item]
            size = stockItem.size

            color = ClothingColor.objects.get(product_id_id=id, color_id=stockItem.color_id).color


            obj = Clothing.objects.get(product_id=id)
            products.append([item, obj, quantity, stock, size, color])

            price = float(obj.price)

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
    
    messages.success(request, 'Cart cleared!')
    return redirect('home')


# Create your views here.
