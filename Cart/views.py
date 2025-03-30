from itertools import product
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import capfirst

from Cart.models import Cart, CartItem
from store.models import Product, Variation

# Create your views here.
def cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
        
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    products_variation = []
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                products_variation.append(variation)
            except:
                pass

    try:
        cart = Cart.objects.get(cart_id=cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = cart_id(request)
        )
    cart.save()
        
    try:
        # First try to find a cart item with the same product and variations
        cart_items = CartItem.objects.filter(product=product, cart=cart)
        if len(products_variation) > 0:
            # If there are variations, find a cart item with the same variations
            for cart_item in cart_items:
                if set(cart_item.variations.all()) == set(products_variation):
                    cart_item.quantity += 1
                    cart_item.save()
                    return redirect('cart')
            # If no matching cart item found, create a new one
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart
            )
            for item in products_variation:
                cart_item.variations.add(item)
            cart_item.save()
        else:
            # If no variations, just increment quantity of existing cart item
            cart_item = cart_items.first()
            cart_item.quantity += 1
            cart_item.save()
    except CartItem.DoesNotExist:
        # Create new cart item if none exists
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
        if len(products_variation) > 0:
            for item in products_variation:
                cart_item.variations.add(item)
        cart_item.save()
    return redirect('cart')

def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=cart_id(request))
    product = get_object_or_404(Product,id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    
    if(cart_item.quantity > 1):
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
        
    return redirect('cart')


def delete_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    
    # Get all cart items for this product
    cart_items = CartItem.objects.filter(product=product, cart=cart)
    
    # If there's only one cart item, delete it
    if cart_items.count() == 1:
        cart_items.first().delete()
    else:
        # If there are multiple cart items, we need to handle variations
        products_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    products_variation.append(variation)
                except:
                    pass
        
        # Find and delete the cart item with matching variations
        for cart_item in cart_items:
            if set(cart_item.variations.all()) == set(products_variation):
                cart_item.delete()
                break
    
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    try:
        cart = Cart.objects.get(cart_id=cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'cart.html', context)

def checkout(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    try:
        cart = Cart.objects.get(cart_id=cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    
    return render(request, 'checkout.html', context)
