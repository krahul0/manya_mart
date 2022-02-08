from datetime import datetime
from .forms import OrderForm

from django.shortcuts import render, redirect
# from django.http import  HttpResponse,JsonResponse

from cart.models import CartItem


import json
from .models import Order


from django.shortcuts import render,redirect
from django.http import  HttpResponse,JsonResponse
from cart.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order,Payment,OrderProduct
import json
# from store.models import Product

def payments(request):
    return render(request,'orders/payments.html')


def place_order(request,total=0,quantity=0):
    current_user = request.user

    #It the cart count is less then or equal to zero then redirect back to shop
    cart_items =CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <=0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total +=(cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    tax=(15 * total)/100
    grand_total =total +tax
    print('siu')



    if request.method == 'POST':
        form =OrderForm(request.POST)
        print('a')
        # return render(request,'store/store.html')

        if form.is_valid():
            print('byue')
            #Store all the billing information inside order table
            data = Order()
            data.user =current_user
            data.first_name =form.cleaned_data['first_name']
            data.last_name =form.cleaned_data['last_name']
            data.email =form.cleaned_data['email']
            data.phone =form.cleaned_data['phone']
            data.address_line_1 =form.cleaned_data['address_line_1']
            data.address_line_2 =form.cleaned_data['address_line_2']
            data.city =form.cleaned_data['city']
            data.state =form.cleaned_data['state']
            data.country =form.cleaned_data['country']
            data.order_note =form.cleaned_data['order_note']
            data.order_total =grand_total
            data.tax = tax
            data.ip =request.META.get('REMOTE_ADDR')
            print('byue')

            data.save()
            print('re')

            #Generate order number
            yr =int(datetime.date.today().strftime('%Y'))
            dt =int(datetime.date.today().strftime('%d'))
            mt =int(datetime.date.today().strftime('%m'))
            d =datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")#20210315
            order_number = current_date +str(data.id)
            data.order_number =order_number
            print('sn')
            data.save()
            print('sd')

            order = Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)
            context={
                'order':order,
                'cart_items':cart_items,
                'total':total,
                'tax':tax,
                'grand_total':grand_total,
            }
            return render(request,'orders/payments.html',context)
    else:
        return redirect('checkout')
