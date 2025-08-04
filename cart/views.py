from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from base.models import Clothing, Order, OrderItem, User, ProductVariant
from django.contrib import messages
import uuid

@login_required(login_url='login')
def cart(request):
    cart = request.session.get('cart', {})
    order_id = request.session.get('order_id')

    if request.method == 'POST':
        total = 0

        for item in cart:
            id = item[:36]
            NewItem = Clothing.objects.get(product_id=id.replace('-', ''))
            price = float(NewItem.price)

            quantity = float(request.POST.get(f'{id}')) if request.POST.get(f'{id}') != None else 0

            print(quantity)

            total += (price * quantity)

        create_order = Order(amount=total, paid=False, 
                        user_id_id=request.user.id,)
        create_order.save()

        for item in cart:
            id = item[:36]

            try:
                pos_id = item.index(':')
                id = item[:pos_id]

                size_col = item[pos_id+1:]
                
                try:    
                    pos_color = item.index(';')

                    size = item[pos_id+1:pos_color]
                    color_id = item[pos_color+1:]

                    if color_id != '':
                        stockItem = ProductVariant.objects.get(size=size, 
                                                            color_variant_id=color_id, 
                                                            product_id_id=id)
                        
                    else:
                        stockItem = ProductVariant.objects.get(size=size, 
                                                            product_id_id=id)   

                except:
                    id = item[:pos_id]

                    stockItem = ProductVariant.objects.get(size=size_col, product_id_id=id)

            except:
                try:
                    color_id = item.index(';')
                    id = item[:color_id]

                    color_id = item[color_id+1:]

                    stockItem = ProductVariant.objects.get(color_variant_id=color_id, product_id_id=id)

                except:
                    id = item

                    stockItem = ProductVariant.objects.get(product_id_id=id)


            NewItem = Clothing.objects.get(product_id=id)
            
            price = float(NewItem.price)

            order_item = OrderItem(purchase_id=create_order.purchase_id,
                                   product_id_id=id.replace('-', ''),
                                   user_id_id=request.user.id,
                                   quantity=int(cart[item]),
                                   purchase_price=price,
                                   variant_id_id=stockItem.variant_id)
            
            order_item.save()
            

        print('total')
        print(total)

        request.session['total'] = float(total)
        

        request.session['order_id'] = str(create_order.purchase_id)

        return redirect('checkout')



    else:
        '''
        if request.method == 'GET' and 'update_cart' in request.GET:
            total = 0
            products = []

            for item in cart:
                pos_id = item.index(":")
                id = item[:pos_id].replace('-', '')
                size=item[(pos_id+1):]

                print(id)

                new_quantity = request.GET.get(f'{id}')

                print(new_quantity)

                request.session['cart'][id] = new_quantity
                
                priceObj = Clothing.objects.get(product_id=id)
                price = float(priceObj.price)

                products.append([priceObj, new_quantity, priceObj.stock, size])

                total += price
                
                context = {'products': products,
                           'cart': request.session.get('cart', {}),
                           'total': total}

                return render(request, 'cart/cart.html', context)

                
        else:
        '''
        products = []
        total = 0

        for item in cart:
            # 59c559f5-37fd-489d-aae1-453cecd9d335:29;59c559f5-37fd-489d-aae1-453cecd9d335

            try:
                pos_id = item.index(':')
                id = item[:pos_id]

                size_col = item[pos_id+1:]
                
                try:    
                    pos_color = item.index(';')

                    size = item[pos_id+1:pos_color]
                    color_id = item[pos_color+1:]            
                    
                    print('130')

                    if color_id != '':
                        stockItem = ProductVariant.objects.get(size=size, color_variant_id=color_id, product_id_id=id)

                    else:
                        stockItem = ProductVariant.objects.get(size=size, product_id_id=id)


                except:
                    id = item[:pos_id]
                    print('134')
                    stockItem = ProductVariant.objects.get(size=size_col, product_id_id=id)


            except:
                try:
                    color_id = item.index(';')
                    id = item[:color_id]

                    color_id = item[color_id+1:]
                    print('145')
                    stockItem = ProductVariant.objects.get(color_variant_id=color_id, product_id_id=id)

                except:
                    id = item
                    print(item)
                    print('151')
                    stockItem = ProductVariant.objects.get(product_id_id=id)
            
            # {% for item, qty, stock, size in products %}
            print(stockItem)

            stock = stockItem.stock
            size = stockItem.size
            quantity = cart[item]


            obj = Clothing.objects.get(product_id=id)

            products.append([obj, quantity, stock, size])

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
