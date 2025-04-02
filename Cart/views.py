from itertools import product
from django.contrib.auth.decorators import login_required
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
        if request.user.is_authenticated:
            # For authenticated users, get or create cart item directly
            cart_items = CartItem.objects.filter(product=product, user=request.user)
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
                    user=request.user
                )
                for item in products_variation:
                    cart_item.variations.add(item)
                cart_item.save()
            else:
                # If no variations, just increment quantity of existing cart item
                if cart_items.exists():
                    cart_item = cart_items.first()
                    cart_item.quantity += 1
                    cart_item.save()
                else:
                    cart_item = CartItem.objects.create(
                        product=product,
                        quantity=1,
                        user=request.user
                    )
                    cart_item.save()
        else:
            # For non-authenticated users, use session-based cart
            try:
                cart = Cart.objects.get(cart_id=cart_id(request))
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    cart_id=cart_id(request)
                )
            cart.save()
            
            try:
                cart_items = CartItem.objects.filter(product=product, cart=cart)
                if len(products_variation) > 0:
                    for cart_item in cart_items:
                        if set(cart_item.variations.all()) == set(products_variation):
                            cart_item.quantity += 1
                            cart_item.save()
                            return redirect('cart')
                    cart_item = CartItem.objects.create(
                        product=product,
                        quantity=1,
                        cart=cart
                    )
                    for item in products_variation:
                        cart_item.variations.add(item)
                    cart_item.save()
                else:
                    if cart_items.exists():
                        cart_item = cart_items.first()
                        cart_item.quantity += 1
                        cart_item.save()
                    else:
                        cart_item = CartItem.objects.create(
                            product=product,
                            quantity=1,
                            cart=cart
                        )
                        cart_item.save()
            except CartItem.DoesNotExist:
                cart_item = CartItem.objects.create(
                    product=product,
                    quantity=1,
                    cart=cart
                )
                if len(products_variation) > 0:
                    for item in products_variation:
                        cart_item.variations.add(item)
                cart_item.save()
    except Exception as e:
        print(f"Error in add_cart: {str(e)}")
        return redirect('cart')
        
    return redirect('cart')

def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            # Retrieve the cart item for authenticated users
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            # Retrieve the cart item for unauthenticated users (session-based cart)
            cart = Cart.objects.get(cart_id=cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

        # Decrement the quantity or delete the cart item
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except CartItem.DoesNotExist:
        # Log the error for debugging
        print(f"CartItem with id {cart_item_id} does not exist.")
    except Cart.DoesNotExist:
        # Log the error for debugging
        print(f"Cart with id {cart_id(request)} does not exist.")
    except Exception as e:
        # Log any other exceptions
        print(f"Error in remove_cart: {str(e)}")

    return redirect('cart')

def delete_cart_item(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    try:
        if request.user.is_authenticated:
            # For authenticated users, get cart items by user
            cart_items = CartItem.objects.filter(product=product, user=request.user)
        else:
            # For non-authenticated users, get cart items by session cart
            cart = Cart.objects.get(cart_id=cart_id(request))
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
    except Cart.DoesNotExist:
        print(f"Cart with id {cart_id(request)} does not exist.")
    except Exception as e:
        print(f"Error in delete_cart_item: {str(e)}")
    
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
   
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated: 
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
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
@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    try:
        if request.user.is_authenticated: 
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
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
