from django.shortcuts import render, redirect
from .forms import UserRegisterForm, UserProfileForm
from django.contrib import messages

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
            messages.success(request,f'profile updated')
            return redirect('user')
    else:
        u_form = UserRegisterForm()
        p_form = UserProfileForm()

    content = {
        'u_form':u_form,
        'p_form':p_form,
    }

    return render(request, 'users/register.html',content)