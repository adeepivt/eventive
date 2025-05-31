from django import forms
from django.contrib.auth.models import User
# from bootstrap_datepicker_plus import DatePickerInput
from bootstrap_datepicker_plus.widgets import DateTimePickerInput
from .models import Event, Booking, Review


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

class EventReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['body','rating']

    def __init__(self, *args, **kwargs):
        super(EventReviewForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class AvailabilityForm(forms.Form):
    event_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'onclick': 'this.showPicker();',
        }),
        label='Event Date'
    )
    event_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control'
        }),
        label='Event Time',
        required=False
    )
    # duration_hours = forms.IntegerField(
    #     min_value=1,
    #     max_value=24,
    #     initial=4,
    #     widget=forms.NumberInput(attrs={
    #         'class': 'form-control',
    #         'min': '1',
    #         'max': '24'
    #     }),
    #     label='Duration (hours)'
    # )
    # guest_count = forms.IntegerField(
    #     min_value=1,
    #     widget=forms.NumberInput(attrs={
    #         'class': 'form-control',
    #         'min': '1'
    #     }),
    #     label='Number of Guests'
    # )

# class EventBookingForm(forms.ModelForm):
#     class Meta:
#         model = Booking
#         fields = ['start_date','end_date']

#     def __init__(self, *args, **kwargs):
#         super(EventBookingForm, self).__init__(*args, **kwargs)
#         for visible in self.visible_fields():
#             visible.field.widget.attrs['placeholder'] = 'choose ' +visible.name
#             visible.field.widget.attrs['class'] = 'datepicker form-control'
#             visible.field.widget.attrs['readonly'] = 'readonly'
#             visible.field.widget.attrs['style'] = 'background-color:white'

class BookingForm(forms.ModelForm):
    customer_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name'
        })
    )
    customer_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    customer_phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number'
        })
    )
    # guest_count = forms.IntegerField(
    #     min_value=1,
    #     widget=forms.NumberInput(attrs={
    #         'class': 'form-control',
    #         'placeholder': 'Number of guests'
    #     })
    # )
    special_requests = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any special requests or notes...'
        })
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'onclick': 'this.showPicker();',
            'hx-get':".",
            'hx-trigger':"change, input delay:200ms",
            'hx-target':"#date-display",
            'hx-swap':"innerHTML",
            'hx-include':"this",
            'hx-headers':'{"X-Date-Update": "true"}'
        }),
        label='Start Date'
    )
    
    class Meta:
        model = Booking
        fields = ['customer_name', 'customer_email', 'customer_phone', 'special_requests']