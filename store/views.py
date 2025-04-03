from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from Cart.models import CartItem
from Cart.views import cart_id
from category.models import Category
from store.models import Product, Variation

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
        
        # Get variations for the specific product
        colors = Variation.objects.filter(product=single_product, variation_category__iexact='color')
        sizes = Variation.objects.filter(product=single_product, variation_category__iexact='size')
        
    except Exception as error:
        raise error
    
    context = {
        "product": single_product, 
        'in_cart': in_cart,
        'colors': colors,
        'sizes': sizes,
    }
    
    return render(request=request, template_name="single_product.html", context=context)
    
def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(product_description__icontains=keyword) | Q(product_name__icontains=keyword))
    
    products_count = products.count()
    context = {'products': products, 'products_count': products_count}
    return render(request=request, template_name="store.html", context=context)