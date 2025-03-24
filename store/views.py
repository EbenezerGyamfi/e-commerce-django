
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from Cart.models import CartItem
from Cart.views import cart_id
from category.models import Category
from store.models import Product

# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None
    
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available = True)
        paginator = Paginator(products, 1)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
        
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        # Fetch all products with is_available=
        
        paginator = Paginator(products, 3)
        
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
        
    context = {'products' : paged_products, 'product_count': product_count}
        
    return render(request=request, template_name="store.html", context=context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=cart_id(request), product=single_product).exists()
    except Exception as error:
        raise error
    
    context = {"product": single_product, 'in_cart': in_cart}
    
    
    return render(request=request, template_name="single_product.html", context=context)
    
    