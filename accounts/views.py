from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from bookings.models import Booking, BookingDoctor

from .models import Account, UserProfile
from django.contrib import messages, auth
from .forms import RegistrationForm, UserForm, UserProfileForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import requires_csrf_token

#verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.models import Cart, CartItem
from carts.views import _cart_id
from team.models import Doctor
import requests



# Create your views here.
@requires_csrf_token
def register(request):

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password )
            user.phone_number=phone_number
            user.save()

            # Create a user profile
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'default/default-user.png'
            profile.save()

            #USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)), #encodes user's primary key
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()


            #messages.success(request, 'Success! Verification email has been sent to your registered email id [email id] for account activation')
            return redirect('/accounts/login/?command=verification&email='+email)

    else:
        form = RegistrationForm()

    context = {
        'form': form
    }
    return render(request, 'accounts/register.html', context)

@requires_csrf_token
def login(request):

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:

            try:
                cart = Cart.objects.get(cart_id = _cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    #getting the doctor slots by cart id
                    doctor_slot = []
                    for item in cart_item:
                        slot = item.slots.all()
                        doctor_slot.append(list(slot))

                    #get the cart items from the user to access his product variation
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_slot = item.slots.all()
                        ex_var_list.append(list(existing_slot))
                        id.append(item.id)

                    #get the common doctor slot between doctor_slot list and ex_var list

                    for i in doctor_slot:
                        if i in ex_var_list:
                            index = ex_var_list.index(i)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.frequency += 1
                            item.user = user
                            item.save()

                        else:
                            cart_item=CartItem.objects.filter(cart=cart)

                            for item in cart_item:
                                item.user = user
                                item.save()

            except:
                pass

            auth.login(request, user)
            messages.success(request, 'You are now  logged in.')
            url = request.META.get(('HTTP_REFERER')) #grabs the previous url from which you are reirected
            try:
                query = requests.utils.urlparse(url).query
                print('query ->', query)
                # next =/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                #print('params ->', params)

                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)

            except:
                return redirect('dashboard')

        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    
    return render(request, 'accounts/login.html')


@login_required(login_url = 'login') #decorator 
def logout(request):

    auth.logout(request)
    messages.success(request, 'You are logged out')
    return redirect('login')

def activate(request, uidb64, token): #decode encoded uid and set user is_active status to true
    try:
        uid = urlsafe_base64_decode(uidb64).decode() #decodes uidb abd stores primary key to uid
        user = Account._default_manager.get(pk=uid)
    
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account is activated.')
        return redirect('login')
    
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')

@login_required(login_url = 'login') #decorator 
def dashboard(request):

    bookings = Booking.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    bookings_count = bookings.count()
    

    userprofile = UserProfile.objects.get(user_id=request.user.id)
    context = {
        'bookings_count': bookings_count,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/dashboard.html', context)

@requires_csrf_token
def forgotPassword(request):
    
    if request.method == 'POST':
        email = request.POST['email']

        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)), #encodes user's primary key
                'token': default_token_generator.make_token(user),
                })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')


        else:
            messages.error(request, "Account doesn't exist!")
            return redirect('forgotPassword')

    return render(request, 'accounts/forgotPassword.html')

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode() #decodes uidb abd stores primary key to uid
        user = Account._default_manager.get(pk=uid)
    
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid #reset password will validate based on uid of the session
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')

    else:
        messages.error(request, 'This link has expired!')
        return redirect('login')

@requires_csrf_token
def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password) #using set_password ensures that your password is hashed and saved
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')

        
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('resetPassword')

    else:
        return render(request, 'accounts/resetPassword.html')

@login_required(login_url = 'login') #decorator
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'bookings' : bookings,
    }
    return render(request, 'accounts/my_bookings.html', context)

@login_required(login_url = 'login') #decorator
def edit_profile(request):

    userprofile = get_object_or_404(UserProfile, user=request.user)

    if request.method =='POST':
        user_form = UserForm(request.POST, instance=request.user) #instance is being used to update the user profile by passing instance we can see the existing details
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')

    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    context = {
        'user_form' : user_form,
        'profile_form' : profile_form,
        'userprofile' : userprofile
    }

    return render(request, 'accounts/edit_profile.html', context)

@login_required(login_url = 'login') #decorator
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, 'Password updated successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')

@login_required(login_url = 'login') #decorator
def booking_detail(request, booking_id):
    booking_detail = BookingDoctor.objects.filter(booking__booking_number=booking_id)
    booking = Booking.objects.get(booking_number=booking_id)

    subtotal = 0
    for i in booking_detail:
        subtotal += i.doctor_price * i.frequency
    
    context = {
        'booking_detail' : booking_detail,
        'booking' : booking,
        'subtotal': subtotal,

    }
    return render(request, 'accounts/booking_detail.html', context)

