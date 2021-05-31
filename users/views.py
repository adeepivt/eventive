from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from .forms import UserRegisterForm, UserProfileForm, VendorLoginForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
from events.models import Event
from .models import Profile

# Create your views here.

def user_register(request):
    if request.method == 'POST':
        u_form = UserRegisterForm(request.POST)
        p_form = UserProfileForm(request.POST)
        if u_form.is_valid() and p_form.is_valid():
            new_user = u_form.save()
            profile = p_form.save(commit=False)
            if profile.user_id is None:
                profile.user_id = new_user.id
            profile.save()
            messages.success(request,f'profile created')
            return redirect('login')
    else:
        u_form = UserRegisterForm()
        p_form = UserProfileForm()

    content = {
        'u_form':u_form,
        'p_form':p_form,
    }

    return render(request, 'users/register.html',content)

def user_login(request):
    if request.method == 'POST':
        valuenext= request.POST.get('next')
        username = request.POST['username']
        password = request.POST['password']
        account = authenticate(username=username, password=password)
        if account is not None:
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

def vendor_register(request):
    if request.method == 'POST':
        u_form = UserRegisterForm(request.POST)
        v_form = UserProfileForm(request.POST)
        if u_form.is_valid() and v_form.is_valid():
            new_user = u_form.save()
            profile = v_form.save(commit=False)
            if profile.user_id is None:
                profile.user_id = new_user.id
                profile.is_admin = True
            profile.save()
            messages.success(request,f'profile created')
            return redirect('vendor_login')
    else:
        u_form = UserRegisterForm()
        v_form = UserProfileForm()

    content = {
        'u_form':u_form,
        'v_form':v_form,
    }

    return render(request, 'users/vendor_register.html', content)


def vendor_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        account = authenticate(username=username, password=password)
        if account is not None:
            if account.profile.is_admin:
                login(request, account)
                return redirect('event-home')
            messages.warning(request,f'username or password is incorrect')
        else:
            messages.warning(request,f'username or password is incorrect')
    
    form = VendorLoginForm()

    context = {'form':form}

    return render(request, 'users/vendor.html', context)
