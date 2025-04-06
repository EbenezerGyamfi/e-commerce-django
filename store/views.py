from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from Cart.models import CartItem
from Cart.views import cart_id
from category.models import Category
from orders.models import OrderProduct
from store.forms import ReviewForm
from store.models import Product, ProductGallery, ReviewRating, Variation


# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 1)
        page = request.GET.get("page")
        paged_products = paginator.get_page(page)
        product_count = products.count()

    else:
        products = Product.objects.all().filter(is_available=True).order_by("id")
        # Fetch all products with is_available=

        paginator = Paginator(products, 3)

        page = request.GET.get("page")
        paged_products = paginator.get_page(page)
        product_count = products.count()

    context = {"products": paged_products, "product_count": product_count}

    return render(request=request, template_name="store.html", context=context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(
            category__slug=category_slug, slug=product_slug
        )
        in_cart = CartItem.objects.filter(
            cart__cart_id=cart_id(request), product=single_product
        ).exists()

        # Get variations for the specific product
        colors = Variation.objects.filter(
            product=single_product, variation_category__iexact="color"
        )
        sizes = Variation.objects.filter(
            product=single_product, variation_category__iexact="size"
        )
        reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
        
        # Get product gallery images
        product_gallery = ProductGallery.objects.filter(product_id=single_product.id)
        

    except Exception as error:
        raise error

    # check if user has already purchased the product
    if request.user.is_authenticated:
        try:
            ordered_product = OrderProduct.objects.filter(
                product_id=single_product.id, user_id=request.user.id
            ).exists()
        except OrderProduct.DoesNotExist:
            ordered_product = None
    else:
        ordered_product = None

    # Get the reviews for the product

    context = {
        "product": single_product,
        "in_cart": in_cart,
        "colors": colors,
        "sizes": sizes,
        "ordered_product": ordered_product,
        "reviews": reviews,
        "product_gallery": product_gallery,
    }

    return render(request=request, template_name="single_product.html", context=context)


def search(request):
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            products = Product.objects.order_by("-created_date").filter(
                Q(product_description__icontains=keyword)
                | Q(product_name__icontains=keyword)
            )

    products_count = products.count()
    context = {"products": products, "products_count": products_count}
    return render(request=request, template_name="store.html", context=context)


def submit_review(request, product_id):
    url = request.META.get("HTTP_REFERER")
    if request.method == "POST":
        try:
            reviews = ReviewRating.objects.get(
                user__id=request.user.id, product__id=product_id
            )
            form = ReviewForm(
                request.POST, instance=reviews
            )  # the instance will make sure you update the review if review already exist
            form.save()
            messages.success(request, "Thank you for your review.")
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data["subject"]
                data.review = form.cleaned_data["review"]
                data.rating = form.cleaned_data["rating"]
                data.ip = request.META.get("REMOTE_ADDR")
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, "Thank you for your review.")
                return redirect(url)
            else:
                messages.error(request, "Error submitting your review.")
                return redirect(url)
    return redirect(url)
