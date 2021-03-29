from django.shortcuts import render, redirect
from .forms import VendorRegisterForm, UserRegisterForm
from django.contrib import messages

# Create your views here.

def vendor_register(request):
    if request.method == 'POST':
        u_form = UserRegisterForm(request.POST)
        v_form = VendorRegisterForm(request.POST)
        if u_form.is_valid() and v_form.is_valid():
            new_user = u_form.save()
            profile = v_form.save(commit=False)
            if profile.user_id is None:
                profile.user_id = new_user.id
                profile.is_admin = True
                my_group.user_set.add(profile.user)
            profile.save()
            messages.success(request,f'profile updated')
            return redirect('vendor_register')
    else:
        u_form = UserRegisterForm()
        v_form = VendorRegisterForm()

    content = {
        'u_form':u_form,
        'v_form':v_form,
    }

    return render(request, 'vendors/vendor_register.html', content)