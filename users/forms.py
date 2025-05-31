from django import forms
from .models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username','email')

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if visible.name == 'password1':
                visible.field.widget.attrs['placeholder'] = 'password'
            elif visible.name == 'password2':
                visible.field.widget.attrs['placeholder'] = 'confirm Password'
            else:
                visible.field.widget.attrs['placeholder'] = visible.name

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['mobile','location','img']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['placeholder'] = visible.name

class CustomAuthForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(CustomAuthForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['placeholder'] = visible.name

class VendorLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(VendorLoginForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['placeholder'] = visible.name
            visible.field.widget.attrs['autocomplete'] = "off"
            visible.field.widget.attrs['autofocus'] = "off"