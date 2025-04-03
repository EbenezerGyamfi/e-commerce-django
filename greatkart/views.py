from django.shortcuts import render

from store.models import Product


def home(request):
    context = {"products": Product.products()}
    return render(request, "home.html", context=context)
