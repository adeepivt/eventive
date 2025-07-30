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
        widgets = {
                'mobile': forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter your mobile number (min 10 digits)',
                    'pattern': '[0-9]{10,}',
                    'title': 'Enter a valid mobile number (minimum 10 digits)'
                }),
        }

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

class UserUpdateForm(forms.ModelForm):
    """Form for updating basic user information"""
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
    
    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['placeholder'] = visible.name.replace('_', ' ').title()
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email is already taken by another user
            if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("This email is already in use.")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            # Check if username is already taken by another user
            if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("This username is already taken.")
        return username