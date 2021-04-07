from django import forms
from django.contrib.auth.models import User
from bootstrap_datepicker_plus import DatePickerInput
from .models import Event, Booking


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


class DateInput(forms.DateInput):
    input_type = 'date'

class EventBookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['start_date','end_date']

    def __init__(self, *args, **kwargs):
        super(EventBookingForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget = DateInput()
            visible.field.widget.attrs['placeholder'] = visible.name
            visible.field.widget.attrs['class'] = 'datepicker'