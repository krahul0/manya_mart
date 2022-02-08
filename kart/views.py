from django.shortcuts import render
from django.db.models import Count
from category.models import Category

from store.models import Product


def home(request):
        products = Product.objects.all().filter(is_available=True).order_by('created_date')


        context = {
           'products': products,
         }

        return render(request,'home.html',context)