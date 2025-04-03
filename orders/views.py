import datetime
import json
from re import sub
from django.core.mail import EmailMessage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string

from Cart.models import CartItem
from orders.forms import OrderForm
from orders.models import Order, OrderProduct, Payment
from store.models import Product


def place_order(
    request,
    total=0,
    quantity=0,
):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect("store")

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += cart_item.product.price * cart_item.quantity
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data["first_name"]
            data.last_name = form.cleaned_data["last_name"]
            data.phone = form.cleaned_data["phone"]
            data.email = form.cleaned_data["email"]
            data.address_line_1 = form.cleaned_data["address_line_1"]
            data.address_line_2 = form.cleaned_data["address_line_2"]
            data.country = form.cleaned_data["country"]
            data.state = form.cleaned_data["state"]
            data.city = form.cleaned_data["city"]
            data.order_note = form.cleaned_data["order_note"]
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get("REMOTE_ADDR")
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime("%Y"))
            dt = int(datetime.date.today().strftime("%d"))
            mt = int(datetime.date.today().strftime("%m"))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")  # 20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(
                user=current_user, is_ordered=False, order_number=order_number
            )
            context = {
                "order": order,
                "cart_items": cart_items,
                "total": total,
                "tax": tax,
                "grand_total": grand_total,
            }
            return render(request, "payment.html", context)
    else:
        return redirect("checkout")


def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(
        user=request.user, is_ordered=False, order_number=body["orderID"]
    )
    # store all transaction details inside paymet
    payment = Payment(
        user=request.user,
        payment_id=body["transID"],
        payment_method=body["payment_method"],
        amount_paid=order.order_total,
        status=body["status"],
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()

    # move cart items to order Product table and reduct quantity of the sold products, clear the cart and send order received email to customer,

    cart_items = CartItem.objects.filter(user=request.user)

    for cart_item in cart_items:
        data = OrderProduct()
        data.order_id = order.id
        data.product_id = cart_item.product.id
        data.payment = payment
        data.user_id = request.user.id
        data.quantity = cart_item.quantity
        data.product_price = cart_item.product.price
        data.ordered = True
        data.save()

        cart_items = CartItem.objects.get(id=cart_item.id)

        product_variation = cart_items.variations.all()
        data = OrderProduct.objects.get(id=data.id)

        data.variations.set(product_variation)

        data.save()

        # Reduce the quantity of the sold products
        product = Product.objects.get(id=cart_item.product.id)
        product.stock -= cart_item.quantity
        product.save()
        # Clear the cart of a user

    CartItem.objects.filter(user=request.user).delete()
    # Send order received email to customer
    mail_subject = "Thank you for your order! "
    message = render_to_string(
        "order_recieved_email.html",
        {
            "user": request.user,
            "ordered_products": data,
        },
    )

    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()
    # Send order number and transaction id back to sendData method via JsonResponse

    data = {
        "order_number": order.order_number,
        "transaction_id": payment.payment_id,
    }
    return JsonResponse(data, content_type="application/json")


def order_complete(request):
    order_number = request.GET.get("order_number")
    tranId = request.GET.get("payment_id")

    try:
        order = Order.objects.get(order_number=order_number)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        payment = Payment.objects.get(payment_id=tranId)

        sub_total = 0
        for product in ordered_products:
            sub_total += product.product_price * product.quantity

        context = {
            "order": order,
            "ordered_products": ordered_products,
            "tranID": payment.payment_id,
            "payment": payment,
            "sub_total": sub_total,
        }
        return render(request, "order_complete.html", context=context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect("home")
