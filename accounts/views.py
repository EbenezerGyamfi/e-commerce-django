from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
import requests

from Cart.models import Cart, CartItem
from accounts.forms import RegistrationForm, UserForm, UserProfileForm
from accounts.models import Account, UserProfile
from Cart.views import cart_id
from orders.models import Order, OrderProduct


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data["email"].split("@")[0]
            user.is_active = False
            user.save()

            # Create user profile
            user_profile = UserProfile()
            user_profile.user_id = user
            user_profile.profile_picture = "default/default-profile.png"
            user_profile.save()

            # Send activation email
            current_site = get_current_site(request)
            mail_subject = "Please activate your account"
            message = render_to_string(
                "account_verification_email.html",
                {
                    "user": user,
                    "domain": current_site,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )
            to_email = form.cleaned_data["email"]
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(
                request,
                "Registration successful! Please check your email to activate your account.",
            )
            return redirect("login")
    else:
        form = RegistrationForm()

    context = {
        "form": form,
    }
    return render(request, "register.html", context)


def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=cart_id(request))
                cart_items_exists = CartItem.objects.filter(cart=cart).exists()
                print(cart_items_exists)
                if cart_items_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    for item in cart_item:
                        item.user = user
                        item.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, "Logged in successfully.")
            url = request.META.get(
                "HTTP_REFERER"
            )  # redirect users from where they came from
            print(url)
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split("=") for x in query.split("&"))

                if "next" in params:
                    nextPage = params["next"]
                    return redirect(nextPage)

            except Exception as error:
                return redirect("dashboard")

        else:
            messages.error(request, "Invalid credentials.")
            return redirect("login")

    return render(request, "login.html")


@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("login")


def activate(request, uidb64, token):
    try:
        if not uidb64 or not token:  # Ensure values exist
            raise ValueError("Missing activation parameters")

        uid = urlsafe_base64_decode(uidb64).decode()  # Decode UID
        user = Account.objects.get(pk=uid)  # Fetch user
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None  # If decoding fails or user doesn't exist, set to None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Account activated successfully.")
        return redirect("login")
    else:
        messages.error(request, "Activation link is invalid or expired.")
        return redirect("login")


@login_required(login_url="login")
def dashboard(request):
    return render(request, "dashboard.html")


def forgot_passowrd(request):
    if request.method == "POST":
        email = request.POST["email"]
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            current_site = get_current_site(request=request)
            mail_subject = "Reset Your Password"
            message = render_to_string(
                "reset-password-email.html",
                {
                    "user": user,
                    "domain": current_site,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )

            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(
                request=request,
                message="password reset. email has been sent to your email",
            )
            return redirect(
                "resetPassword"
            )  # Redirect to login page on successful password reset email sent.  # Redirect to login page on successful password reset email sent.  # Redirect to login page on successful password reset email sent.  # Redirect to login page on successful password reset email sent.  # Redirect to login page on successful password reset email sent.  # Redirect to login page on successful password reset email sent.  # Redirect to login page on successful password reset email sent.  # Redirect to
        else:
            messages.error(request, "Email does not exist.")
            return redirect("forgot-password")

    return render(request, "forgot-password.html")


def resetpassword_validate(request, uidb64, token):
    try:
        if not uidb64 or not token:  # Ensure values exist
            raise ValueError("Missing activation parameters")

        uid = urlsafe_base64_decode(uidb64).decode()  # Decode UID
        user = Account.objects.get(pk=uid)  # Fetch user
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None  # If decoding fails or user doesn't exist, set to None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.success(request, "Please reset your password")
        return redirect("resetPassword")
    else:
        messages.error(request, "Reset password link is invalid or expired.")
        return redirect("resetPassword")


def resetPassword(request):
    if request.method == "POST":
        uid = request.session.get("uid")
        user = Account.objects.get(pk=uid)
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        if password == confirm_password:
            user.set_password(password)
            user.save()
            messages.success(request, "Password reset successfully")
            return redirect("login")
        else:
            messages.error(request, "Passwords do not match")
            return redirect("resetPassword")
    return render(request, "reset-password.html")


@login_required(login_url="login")
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by(
        "-created_at"
    )  # the hyphen will gile result in descending order
    orders_count = orders.count()
    context = {
        "orders": orders,
        "orders_count": orders_count,
    }
    return render(request, "my_orders.html", context=context)


@login_required(login_url="login")
def edit_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":

        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=user_profile
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully")
            return redirect("edit_profile")
        else:
            messages.error(request, "Error updating profile")

    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)
    context = {
        "user_form": user_form,
        "profile_form": profile_form,
        "user_profile": user_profile,
    }
    return render(request, "edit_profile.html", context=context)


@login_required(login_url="login")
def change_password(request):
    if request.method == "POST":
        current_password = request.POST["current_password"]
        new_password = request.POST["new_password"]
        confirm_new_password = request.POST["confirm_password"]

        user = Account.objects.get(username__exact=request.user.username)

        if user.check_password(current_password):
            if new_password == confirm_new_password:
                user.set_password(new_password)
                user.save()

                # auth.logout(request) # by default you will be logged out after changing password
                messages.success(request, "Password changed successfully")
                return redirect("change_password")
            else:
                messages.error(request, "New passwords do not match")
                return redirect("change_password")
        else:
            messages.error(request, "Current password is incorrect")
            return redirect("change_password")

    return render(request, "change-password.html")


def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    
    subtotal = 0
    for order_product in order_detail:
        subtotal += order_product.product_price * order_product.quantity
    # tax = (subtotal * 2) / 100
    
    context = {
        "order_detail": order_detail,
        "order": order,
        'sub_total': subtotal,
        # 'tax': tax,
        # 'total': subtotal + tax,
    }
    return render(request, "order_detail.html", context=context)