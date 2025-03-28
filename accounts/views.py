from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from accounts.forms import RegistrationForm
from accounts.models import Account



def register(request):
    
    if request.method == 'POST':
        
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            #user activation using email verification
            current_site = get_current_site(request=request)
            mail_subject = 'Please activate your account'
            message = render_to_string('account_verification_email.html',{
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            return redirect('/accounts/login/?command=verification&email='+email)
           
            
    else:
        form = RegistrationForm()
        
    context = {'form': form}
    
    return render(request,'register.html', context)
    
    

def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        
        if user is not None:
            auth.login(request, user)
            messages.success(request, 'Logged in successfully.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials.')
            return redirect('login')
        
    return render(request, 'login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('login')

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
        messages.success(request, 'Account activated successfully.')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid or expired.')
        return redirect('login')
@login_required(login_url='login')    
def dashboard(request):
    return render(request, 'dashboard.html')

def forgot_passowrd(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
        
            current_site = get_current_site(request=request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('reset-password-email.html',{
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request=request, message="password reset. email has been sent to your email")
            return redirect('resetPassword')  # Redirect to login page on successful password reset email sent.  # Redirect to login page on successful password reset email sent.  # Redirect to login page on successful password reset email sent.  # Redirect to login page on successful password reset email sent.  # Redirect to login page on successful password reset email sent.  # Redirect to login page on successful password reset email sent.  # Redirect to login page on successful password reset email sent.  # Redirect to
        else:
            messages.error(request, 'Email does not exist.')
            return redirect('forgot-password')
            

                
    return render(request, 'forgot-password.html')

def resetpassword_validate(request,uidb64, token ):
    try:
        if not uidb64 or not token:  # Ensure values exist
            raise ValueError("Missing activation parameters")

        uid = urlsafe_base64_decode(uidb64).decode()  # Decode UID
        user = Account.objects.get(pk=uid)  # Fetch user
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None  # If decoding fails or user doesn't exist, set to None
    
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, "Please reset your password")
        return redirect('resetPassword')
    else:
        messages.error(request, 'Reset password link is invalid or expired.')
        return redirect('resetPassword')
def resetPassword(request):
    if request.method == 'POST':
        uid = request.session.get('uid')
        user = Account.objects.get(pk=uid)
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            user.set_password(password)
            user.save()
            messages.success(request, "Password reset successfully")
            return redirect('login')
        else:
            messages.error(request, "Passwords do not match")
            return redirect('resetPassword')
    return render(request, 'reset-password.html')