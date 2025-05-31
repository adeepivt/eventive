from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, HttpResponseRedirect
from django.http import HttpResponseForbidden
from .forms import UserRegisterForm, UserProfileForm, VendorLoginForm
from django.contrib.auth import authenticate, login
from .models import Profile, PasswordReset
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.mail import EmailMessage
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from events.models import Event
from events.models import Booking
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

# Create your views here.

def user_register(request):
    if request.method == 'POST':
        u_form = UserRegisterForm(request.POST)
        p_form = UserProfileForm(request.POST, request.FILES)
        if u_form.is_valid() and p_form.is_valid():
            new_user = u_form.save()
            profile = p_form.save(commit=False)
            if profile.user_id is None:
                profile.user_id = new_user.id
            profile.save()
            messages.success(request,f'profile created successfully!')
            return redirect('login')
    else:
        u_form = UserRegisterForm()
        p_form = UserProfileForm()

    content = {
        'u_form':u_form,
        'p_form':p_form,
        'user_type':'customer'
    }

    return render(request, 'users/register.html',content)


def user_login(request):
    if request.method == 'POST':
        valuenext= request.POST.get('next')
        username = request.POST['username']
        password = request.POST['password']
        account = authenticate(username=username, password=password)
        if account is not None:
            if not account.is_staff:
                if account.profile.is_admin:
                        messages.warning(request,f'username or password is incorrect')
                else:
                    if valuenext == '':
                        login(request, account)
                        return redirect('event-home')
                    else:
                        login(request, account)
                        return redirect(valuenext)
            else:
                messages.warning(request, 'Username or password is incorrect')
        else:
            messages.warning(request,f'username or password is incorrect')

    form = VendorLoginForm()
    context = {'form':form}
    return render(request, 'users/login.html', context)

def acc_details(request):
    user = request.user
    profile = Profile.objects.get(user=user.id)
    content = {
        'profile' : profile
    }
    return render(request, 'users/profile.html', content)


def vendor_register(request):
    if request.method == 'POST':
        u_form = UserRegisterForm(request.POST)
        v_form = UserProfileForm(request.POST, request.FILES)
        if u_form.is_valid() and v_form.is_valid():
            new_user = u_form.save(commit=False)
            new_user.is_active = False
            new_user.save()
            profile = v_form.save(commit=False)
            if profile.user_id is None:
                profile.user_id = new_user.id
                profile.is_admin = True
                profile.user_type = 'vendor'
                profile.approval_status = 'pending'
            profile.save()
            messages.success(request, 'Thank you for registering! Your vendor' \
                    ' account is now pending approval. You will be notified once it has been reviewed.')
            print(new_user.is_active)
            return redirect('vendor_login')
    else:
        u_form = UserRegisterForm()
        v_form = UserProfileForm()

    content = {
        'u_form':u_form,
        'v_form':v_form,
        'user_type':'vendor'
    }

    return render(request, 'users/register.html', content)


def vendor_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.get(username=username)
            
            if user.check_password(password):
                if hasattr(user, 'profile') and user.profile.is_admin:
                    if user.is_active:
                        login(request, user)
                        return redirect('event-home')
                    else:
                        messages.warning(request, 'Your vendor account is pending approval.')
                else:
                    messages.error(request, 'You are not authorized as a vendor.')
            else:
                messages.error(request, 'Invalid username or password.')
                
        except User.DoesNotExist:
            messages.error(request, 'Invalid username or password.')
            
    form = VendorLoginForm()

    context = {
        'form':form,
        'user_type':'vendor'
        }

    return render(request, 'users/login.html', context)


def ForgotPassword(request):
    email_sent = False 
    sent_to_email = ""

    if request.method == "POST":
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            recent_reset = PasswordReset.objects.filter(
                user=user,
                created_when__gte=timezone.now() - timezone.timedelta(minutes=2)
            ).exists()
            
            if recent_reset:
                messages.info(request, "A password reset link was already sent. Please check your email or wait a few minutes before trying again.")
            else:
                new_password_reset = PasswordReset(user=user)
                new_password_reset.save()

                password_reset_url = reverse('reset-password', kwargs={'reset_id': new_password_reset.reset_id})

                full_password_reset_url = f'{request.scheme}://{request.get_host()}{password_reset_url}'

                email_body = f'Reset your password using the link below:\n\n\n{full_password_reset_url}'
            
                email_message = EmailMessage(
                    'Reset your password', # email subject
                    email_body,
                    settings.EMAIL_HOST_USER, # email sender
                    [email] # email  receiver 
                )

                email_message.fail_silently = True
                email_message.send()
                email_sent = True
                sent_to_email = email
                messages.success(request, f"A password reset link has been sent to {email}.")
            return redirect('password-reset-sent')

        except User.DoesNotExist:
            messages.error(request, f"No user with email '{email}' found")
            return redirect('forgot-password')
    
    context = {
        # 'email_sent': email_sent,
        # 'email': sent_to_email,
    }
    return render(request, 'users/forgot_password.html')

def ResetPassword(request, reset_id):
    try:
        password_reset_id = PasswordReset.objects.get(reset_id=reset_id)

        if request.method == "POST":
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            passwords_have_error = False

            if password != confirm_password:
                passwords_have_error = True
                messages.error(request, 'Passwords do not match')

            expiration_time = password_reset_id.created_when + timezone.timedelta(minutes=10)

            if timezone.now() > expiration_time:
                passwords_have_error = True
                messages.error(request, 'Reset link has expired')

                password_reset_id.delete()
            try:
                validate_password(password, user=password_reset_id.user)  # Pass the user for context
            except ValidationError as e:
                passwords_have_error = True
                for error in e.messages:  # Display all validation errors
                    messages.error(request, error)

            if not passwords_have_error:
                user = password_reset_id.user
                user.set_password(password)
                user.save()

                password_reset_id.delete()

                messages.success(request, 'Password reset. Proceed to login')
                return redirect('login')
            else:
                # redirect back to password reset page and display errors
                return redirect('reset-password', reset_id=reset_id)
    
    except PasswordReset.DoesNotExist:
        
        # redirect to forgot password page if code does not exist
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')

    return render(request, 'users/reset_password.html')

def PasswordResetSent(request):

    if PasswordReset.objects.exists():
        return render(request, 'users/password_reset_sent.html')
    else:
        # redirect to forgot password page if code does not exist
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')

def add_favourites(request, pk):
    event = get_object_or_404(Event, id=pk)
    user = request.user
    if event.favourites.filter(id=user.id).exists():
        event.favourites.remove(request.user)
    else:
        event.favourites.add(request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

def favourites_list(request):
    user = request.user
    if user.profile.is_admin:
         messages.warning(request,f'You are at wrong place!')
    favourites = Event.objects.filter(favourites=request.user)
    return render(request, 'users/favourites.html', {'favourites': favourites})

@login_required
def user_bookings(request):
    """View for users to see their bookings"""
    bookings = Booking.objects.filter(customer=request.user).order_by('-created')
    
    # Add pagination if needed
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'bookings': page_obj,
        'title': 'My Bookings'
    }
    return render(request, 'users/user_bookings.html', context)

@login_required
def booking_detail(request, booking_id):
    """Detailed view of a specific booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if user has permission to view this booking
    if request.user != booking.customer and request.user != booking.event.user:
        return HttpResponseForbidden("You don't have permission to view this booking.")
    
    context = {
        'booking': booking,
    }
    return render(request, 'users/booking_detail.html', context)

@login_required
def vendor_bookings(request):
    """View for vendors to see bookings for their services"""
    try:
        # Assuming you have a way to identify if user is a vendor
        vendor = Event.objects.filter(user=request.user)  # Adjust based on your model
        bookings = Booking.objects.filter(event__in=vendor).order_by('-created')
        
        # Add pagination if needed
        paginator = Paginator(bookings, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'bookings': page_obj,
            'vendor': vendor,
            'title': 'Received Bookings'
        }
        return render(request, 'users/vendor_bookings.html', context)
    except Event.DoesNotExist:

        # Handle case where user is not a vendor
        return render(request, 'users/not_vendor.html')