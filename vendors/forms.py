from django import forms
from users.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username','email')

class VendorRegisterForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['mobile','location']