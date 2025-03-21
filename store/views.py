from django.shortcuts import render

from store.models import Product

# Create your views here.
def store(request):
    products = Product.objects.filter(is_available=True)
    
    context = {'products' : products}
    return render(request=request, template_name="store.html", context=context)