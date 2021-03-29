from django import forms
from django.contrib.auth.models import User
from .models import Event


class EventCreateForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ['user']