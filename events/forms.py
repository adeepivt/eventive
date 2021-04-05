from django import forms
from django.contrib.auth.models import User
from .models import Event


class EventCreateForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ['user']
    
    def __init__(self, *args, **kwargs):
        super(EventCreateForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class EventUpdateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name','place','price','details','image']

    def __init__(self, *args, **kwargs):
        super(EventUpdateForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'