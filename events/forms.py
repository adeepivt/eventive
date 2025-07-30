from django import forms
from django.contrib.auth.models import User
# from bootstrap_datepicker_plus import DatePickerInput
from bootstrap_datepicker_plus.widgets import DateTimePickerInput
from .models import Event, Booking, Review, Facility, EventGallery
from django.forms import modelformset_factory
from django.utils.datastructures import MultiValueDict

class EventCreateForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ['user']

    def __init__(self, *args, **kwargs):
        super(EventCreateForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class EventUpdateForm(forms.ModelForm):
    facilities = forms.ModelMultipleChoiceField(
        queryset=Facility.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'facility-checkbox'
        }),
        required=False,
        help_text="Select all facilities available at your event"
    )
    class Meta:
        model = Event
        fields = ['name','place','price','details','image','facilities']

    def __init__(self, *args, **kwargs):
        super(EventUpdateForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            
        if self.instance and self.instance.pk:
            # This ensures the current facilities are selected when form loads
            self.initial['facilities'] = self.instance.facilities.values_list('id', flat=True)

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

class EventGalleryForm(forms.ModelForm):
    class Meta:
        model = EventGallery
        fields = ['image', 'title', 'description', 'is_featured', 'order']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control', 
                'accept': 'image/*'
            }),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Image title (optional)'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'placeholder': 'Describe this work (optional)'
            }),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Make image field not required for updates (since image already exists)
            if self.instance and self.instance.pk:
                self.fields['image'].required = False


class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        super().__init__(attrs)
        if self.attrs is None:
            self.attrs = {}
        self.attrs['multiple'] = True

    def value_from_datadict(self, data, files, name):
        if isinstance(files, MultiValueDict):
            return files.getlist(name)
        return files.get(name)

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        # Handle multiple files
        if isinstance(data, list):
            result = []
            for item in data:
                if item:
                    result.append(super().clean(item, initial))
            return result
        else:
            file = super().clean(data, initial)
            return [file] if file else []

class MultipleImageUploadForm(forms.Form):
    images = MultipleFileField(
        required=False,
        help_text='Select multiple images to upload (Max: 10 images, 5MB each)'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['images'].widget.attrs.update({
            'class': 'form-control',
            'accept': 'image/*'
        })

    def clean_images(self):
        images = self.cleaned_data.get('images', [])
        
        if not isinstance(images, list):
            images = [images] if images else []
        
        # Remove None values
        images = [img for img in images if img is not None]
        
        if len(images) > 10:
            raise forms.ValidationError("You can upload maximum 10 images at once.")
        
        for image in images:
            if hasattr(image, 'size') and image.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError(f"Image {image.name} is too large. Maximum size is 5MB.")
            
            if hasattr(image, 'content_type') and not image.content_type.startswith('image/'):
                raise forms.ValidationError(f"File {image.name} is not a valid image.")
        
        return images
# Formset for editing existing gallery images
EventGalleryFormSet = modelformset_factory(
    EventGallery,
    form=EventGalleryForm,
    extra=0,
    can_delete=True
)