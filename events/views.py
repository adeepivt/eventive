from django.shortcuts import render, get_object_or_404, redirect
from users.models import Profile
from django.contrib.auth.models import User
from .forms import EventCreateForm, EventUpdateForm, BookingForm, EventReviewForm, AvailabilityForm,EventGalleryForm, MultipleImageUploadForm, EventGalleryFormSet
from .models import Event, Booking, Review, Facility, EventGallery
from django.contrib import messages
from django.views.generic import UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseNotFound, HttpResponse
from django.db.models import Q
from django.db import transaction
import json
from datetime import date
from datetime import datetime, timedelta
from django.views.decorators.http import require_http_methods
from django import forms
# Create your views here.

def home_page(request):
    if request.user.is_authenticated:
        admin = False
        if request.user.profile.is_admin:
            admin = True
            return render(request, 'events/index.html', {'admin' : admin})
        else:
            return render(request, 'events/index.html', {'admin' : admin})
    events = Event.objects.all()
    content = {
        'events':events,
    }

    return render(request, 'events/index.html', content)


@login_required
def event_create(request):
    user = get_object_or_404(User, username=request.user)
    if user.profile.is_admin :
        if request.method == 'POST':
            event_form = EventCreateForm(request.POST, request.FILES)
            upload_form = MultipleImageUploadForm(request.POST, request.FILES)
            if event_form.is_valid():
                instance = event_form.save(commit=False)
                instance.user = user
                instance.save()
                post_added = True
                event_form.save_m2m()
            
                # Handle gallery images
                if upload_form.is_valid():
                    images = upload_form.cleaned_data.get('images', [])
                    for i, image in enumerate(images):
                        EventGallery.objects.create(
                            event=instance,
                            image=image,
                            order=i
                        )
                else:
                    for field, errors in upload_form.errors.items():
                        for error in errors:
                            messages.error(request, f"Gallery: {error}")
                            return render(request, 'events/add_event.html', {
                            'user' : request.user,
                            'e_form': event_form,
                            'upload_form': upload_form
                        })
                return redirect('event-home')
    else:
         
         return HttpResponseNotFound('<h1>404.Page not found</h1>')
    event_form = EventCreateForm()
    upload_form = MultipleImageUploadForm()
    content = {
        'user' : request.user,
        'e_form' : event_form,
        'upload_form': upload_form,
    }
    return render(request, 'events/add_event.html', content)

@login_required
def event_list(request):
    events = Event.objects.filter(user=request.user)

    content = {
        'events':events
    }

    return render(request, 'events/event_list.html', content)

@login_required
def event_details(request, pk):
    user = request.user
    event = Event.objects.get(id=pk)
    image = event.image.url
    reviews = Review.objects.filter(event=pk)
    rating = Review.objects.average_ratings(event)
    user_review = Review.objects.user_review(event,user)
    review_form = EventReviewForm()
    availability_form = AvailabilityForm()
    gallery_images = event.gallery_images.all().order_by(
        'order', '-is_featured', '-uploaded_at'
    )
    if user.profile.is_admin :
        messages.warning(request,"You need customer account")
    else:
        if request.method == 'POST':
            if 'review_submit' in request.POST:
                review_form = EventReviewForm(request.POST)
                print('inside review submit')
                if review_form.is_valid():
                    instance = review_form.save(commit=False)
                    instance.customer = user
                    instance.event = event
                    instance.save()
                    return redirect('event-details', pk=pk)
            elif 'availability_submit' in request.POST:
                print('inside availability submit-----\n\n')
                availability_form = AvailabilityForm(request.POST)
                if availability_form.is_valid():
                    event_date = availability_form.cleaned_data['event_date']
                    event_time = availability_form.cleaned_data.get('event_time')
                    # duration_hours = availability_form.cleaned_data['duration_hours']
                    
                    # Check availability
                    is_available, message = check_event_availability(
                        event, event_date, event_time,
                    )
                    print(is_available, message)
                    print(f"Availability: {is_available}, Message: {message}")
                    # Store result in session to display after redirect
                    request.session['availability_result'] = {
                        'is_available': is_available,
                        'message': message,
                        'date': event_date.strftime('%Y-%m-%d'),
                        'time': event_time.strftime('%H:%M') if event_time else None,
                        # 'duration': duration_hours,
                    }
                    
                    if is_available:
                        messages.success(request, message)
                    else:
                        messages.warning(request, message)
                # else:
                #     messages.error(request, 'Please correct the errors in the availability form.')
            

    content = {
        'user': user,
        'event' : event,
        'img' : image,
        'reviews' : reviews,
        'rating' : rating,
        'user_review' : user_review,
        "review_form" : review_form,
        "availability_form": availability_form,
        'availability_result': request.session.pop('availability_result', None),
        'gallery_images': gallery_images,
        'gallery_count': gallery_images.count(),
        'featured_images': gallery_images.filter(is_featured=True)[:3],
    }
    return render(request, 'events/event_details.html', content)

def check_event_availability(event, event_date, event_time=None, duration_hours=None):
    """
    Check if the event management service is available for the given parameters
    Returns (is_available: bool, message: str)
    """
    
    # Check if the date is in the past
    if event_date < datetime.now().date():
        return False, "Selected date is in the past. Please choose a future date."
    
    # Check guest capacity
    # if hasattr(event, 'max_capacity') and guest_count > event.max_capacity:
    #     return False, f"Guest count exceeds maximum capacity of {event.max_capacity}."
    
    # Check for conflicting bookings
    if event_date:
        start_datetime = event_date
        end_datetime = start_datetime + timedelta(days=1)
        
        # Check for overlapping bookings (adjust query based on your Booking model)
        conflicting_bookings = Booking.objects.filter(
            event=event,
            start_date=event_date,
            # start_date__lt=end_datetime,
            # end_date__gt=start_datetime,
            status__in=['confirmed', 'pending']  # Adjust status values as needed
        )
        print("conflicting_bookings:", conflicting_bookings)
        if conflicting_bookings.exists():
            return False, f"Time slot is not available. The service is already booked on {event_date.strftime('%B %d, %Y')}."
    
    # Check day availability (if you have specific available days)
    weekday = event_date.weekday()
    if hasattr(event, 'available_days'):
        # Assuming available_days is a string like "0,1,2,3,4" for Mon-Fri
        available_days = [int(d) for d in event.available_days.split(',')]
        if weekday not in available_days:
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            return False, f"Service is not available on {day_names[weekday]}s."
    
    # If all checks pass
    return True, f"Great! The service is available on {event_date.strftime('%B %d, %Y')}" + \
                 (f" at {event_time.strftime('%H:%M')}" if event_time else "")


# htmx start

@require_http_methods(["POST"])
def check_availability_htmx(request, event_id):
    """Handle availability check via HTMX - simplified version"""
    event = get_object_or_404(Event, id=event_id)
    event_date = request.POST.get('event_date')
    
    context = {'event': event}
    
    if not event_date:
        context['error'] = 'Please select a date'
    else:
        try:
            # Convert string to date
            selected_date = datetime.strptime(event_date, '%Y-%m-%d').date()
            context['selected_date'] = selected_date
            
            # Check if date is in the past
            if selected_date < datetime.now().date():
                context['error'] = 'Cannot check availability for past dates'
            else:
                # Check availability (simplified - just boolean)
                is_available = check_event_availability(event, selected_date)
                context['is_available'] = is_available[0]
                if is_available[0]:
                    request.session['booking_params'] = {
                        'event_id': event.id, # Store event_id too, for consistency
                        'event_date_str': selected_date.strftime('%Y-%m-%d'),
                    }
                else:
                    # Clear if previous params were set and now it's not available
                    if 'booking_params' in request.session:
                        del request.session['booking_params']
                
        except ValueError:
            context['error'] = 'Invalid date format'
    
    # Return only the results fragment, not the whole page
    return render(request, 'events/availability_result.html', context)



# htmx end 


@login_required
def search_event(request):
    user = request.user
    fav = bool
    l = []
    if user.profile.is_admin:
        messages.warning(request,"You need a customer account")
    else:
        if request.method == 'GET':    
            place =  request.GET.get('place')
            category = request.GET.get('category')
            object_list = Event.objects.filter(
                Q(place__icontains=place) & Q(category__contains=category)
            )
        user_fav = Event.objects.user_favourites(user)
        return render(request, 'events/search_result.html', {'object':object_list, 'fav':user_fav})
    return render(request, 'events/search_result.html')

class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    form_class = EventUpdateForm
    template_name = 'events/event_update.html'
    success_url = reverse_lazy('event-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        
        # Get existing images
        existing_images = EventGallery.objects.filter(event=event)
        
        # Create individual forms for each image
        gallery_forms = []
        for i, image in enumerate(existing_images):
            if self.request.POST:
                form = EventGalleryForm(
                    self.request.POST,
                    self.request.FILES,
                    instance=image,
                    prefix=f'gallery_{i}'
                )
            else:
                form = EventGalleryForm(instance=image, prefix=f'gallery_{i}')
            
            # Add a delete checkbox manually
            form.fields['DELETE'] = forms.BooleanField(required=False, label='Delete this image')
            if self.request.POST:
                form.fields['DELETE'].initial = self.request.POST.get(f'gallery_{i}-DELETE', False)
            
            gallery_forms.append({
                'form': form,
                'image': image,
                'index': i
            })
        
        # Upload form for new images
        if self.request.POST:
            upload_form = MultipleImageUploadForm(self.request.POST, self.request.FILES)
        else:
            upload_form = MultipleImageUploadForm()
        
        context['gallery_forms'] = gallery_forms
        context['upload_form'] = upload_form
        context['existing_count'] = existing_images.count()
        context['max_images'] = EventGallery.MAX_IMAGES_PER_EVENT
        context['remaining_slots'] = max(0, EventGallery.MAX_IMAGES_PER_EVENT - existing_images.count())
        
        return context

    def form_valid(self, form):
        # Check if user owns this event
        if form.instance.user != self.request.user:
            form.add_error(None, 'You need to be the owner to update this event')
            return self.form_invalid(form)

        context = self.get_context_data()
        gallery_forms = context['gallery_forms']
        upload_form = context['upload_form']
        
        # Collect all form validation results
        all_forms_valid = True
        updated_images = []
        images_to_delete = []
        
        # Process each gallery form
        for form_data in gallery_forms:
            gallery_form = form_data['form']
            image_instance = form_data['image']
            
            if gallery_form.is_valid():
                # Check if marked for deletion
                if gallery_form.cleaned_data.get('DELETE', False):
                    images_to_delete.append(image_instance)
                else:
                    # Update the image data
                    updated_image = gallery_form.save(commit=False)
                    updated_image.event = self.object if hasattr(self, 'object') else form.instance
                    updated_images.append(updated_image)
            else:
                all_forms_valid = False
                # Add form errors to context for template display
                for field, errors in gallery_form.errors.items():
                    messages.error(self.request, f"Error in image {form_data['index'] + 1} - {field}: {', '.join(errors)}")

        # Validate upload form
        upload_form_valid = upload_form.is_valid()
        if not upload_form_valid:
            all_forms_valid = False
            for field, errors in upload_form.errors.items():
                messages.error(self.request, f"Upload error - {field}: {', '.join(errors)}")

        if not all_forms_valid:
            return self.form_invalid(form)

        # If all forms are valid, save everything in a transaction
        with transaction.atomic():
            # Save the main event form
            self.object = form.save()
            
            # Delete marked images
            for image_to_delete in images_to_delete:
                image_to_delete.delete()  # This will also delete the file due to your delete method
                messages.success(self.request, f'Image deleted successfully')
            
            # Save updated images
            for updated_image in updated_images:
                updated_image.save()
            
            # Handle new image uploads
            new_images = upload_form.cleaned_data.get('images', [])
            if new_images:
                # Check total image count
                current_count = EventGallery.objects.filter(event=self.object).count()
                
                if current_count + len(new_images) > EventGallery.MAX_IMAGES_PER_EVENT:
                    messages.error(self.request, 
                        f'Cannot add {len(new_images)} images. '
                        f'Maximum {EventGallery.MAX_IMAGES_PER_EVENT} images allowed per event. '
                        f'Current count: {current_count}'
                    )
                    return self.form_invalid(form)
                
                # Save new images
                for image in new_images:
                    EventGallery.objects.create(
                        event=self.object,
                        image=image
                    )
                
                messages.success(self.request, f'Added {len(new_images)} new images')
            
            # Check for featured image constraint
            featured_images = EventGallery.objects.filter(event=self.object, is_featured=True)
            if featured_images.count() > 1:
                # Keep only the first one as featured
                featured_images.exclude(id=featured_images.first().id).update(is_featured=False)
                messages.warning(self.request, 'Only one image can be featured. Others have been unmarked.')

        messages.success(self.request, 'Event updated successfully')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'There were errors in your form. Please check and try again.')
        return self.render_to_response(self.get_context_data(form=form))

# class EventDeleteView(LoginRequiredMixin, DeleteView):
#     model = Event
#     template_name = 'events/confirm_delete.html'
#     success_url = reverse_lazy('event-list')

#     def get_object(self, *args, **kwargs):
#         pk = self.kwargs.get('pk')
#         obj = Event.objects.get(pk=pk)
#         if not obj.user == self.request.user:
#             messages.warning(self.request, "You need to be the owner.")
#         return obj

@login_required
def delete_transaction(request, pk):
    event = get_object_or_404(Event, pk=pk, user=request.user)
    event.delete()
    context = {
        'message': f"{event.name} was deleted successfully!"
    }
    return render(request, 'events/confirm_delete.html', context)


# @require_http_methods(["GET", "POST"])
# def booking_form_htmx(request, event_id):
#     """Handle booking form via HTMX"""
#     event = get_object_or_404(Event, id=event_id)
#     booking_params = request.session.get('booking_params')
    
#     if request.method == 'POST':
#         print('inside post method')
#         form = BookingForm(request.POST)
#         event_date = datetime.strptime(booking_params.get('event_date_str'), '%Y-%m-%d').date() if booking_params else None
        
#         if form.is_valid():
#             if form.cleaned_data['start_date']:
#                 event_date = form.cleaned_data['start_date']
#             try:
#                 is_available, message = check_event_availability(
#                     event, 
#                     event_date, 
#                 )
                
#                 if not is_available:
#                     print(f"Event not available: {message}")  # Debug print
                    
#                     # Add the error message to the form
#                     form.add_error(None, message)
                    
#                     # Debug: Check if we're in HTMX request
#                     print(f"HX-Request: {request.headers.get('HX-Request')}")
                    
#                     # Return the form with error message
#                     context = {
#                         'form': form,
#                         'event': event,
#                         'selected_date': event_date,
#                         'error_message': message,
#                         'is_htmx': request.headers.get('HX-Request')
#                     }
#                     print(f"Context data: {context}")  # Debug print
                    
#                     return render(request, 'events/booking_form.html', context)
                
#                 # Create the booking
#                 booking = form.save(commit=False)
#                 booking.customer = request.user if request.user.is_authenticated else None
#                 booking.event = event
#                 booking.start_date = event_date
#                 print(booking.start_date, booking.end_date, 'start and end date')
#                 booking.status = 'pending'  # or 'confirmed' based on your workflow
                
#                 # Set user if authenticated
#                 if request.user.is_authenticated:
#                     booking.user = request.user
                
#                 booking.save()
                
#                 # Clear session data to prevent resubmission
#                 if 'booking_params' in request.session:
#                     del request.session['booking_params']
                
#                 # Store booking ID in session for success page
#                 request.session['last_booking_id'] = booking.id
                
#                 # Send confirmation email (optional)
#                 # send_booking_confirmation_email(booking)
                
#                 success_url = reverse('booking_success', kwargs={'booking_id': booking.id})

#                 print(booking,'====================\nbooking newwwwwwwwww created')
#                 # Option 1: Standard Django redirect (HTMX follows this)
#                 return redirect(success_url)
                
#             except ValueError:
#                 form.add_error(None, 'Invalid date format')
        
#         # If form is not valid, return form with errors
#         else:
#             print(form.errors)
#             return render(request, 'events/booking_form.html', {
#                 'form': form,
#                 'event': event,
#                 'selected_date': event_date
#             })
    
#     else:
#         # GET request - show form with pre-filled data
#         initial_data = {}

#         if request.headers.get('HX-Request') and request.headers.get('X-Date-Update'):
#             date_value = request.GET.get('start_date')
            
#             if date_value:
#                 try:
#                     start_date_availability = check_event_availability(event, datetime.strptime(date_value, '%Y-%m-%d').date())
#                     if not start_date_availability[0]:
#                         return HttpResponse(f'<div id="date-display"><i class="fa fa-calendar"></i>❌ {start_date_availability[1]}</div>\
#                                                 <span id="target2" hx-swap-oob="true">❌ {start_date_availability[1]}</span>')
#                     date_obj = datetime.strptime(date_value, '%Y-%m-%d')
#                     formatted_date = date_obj.strftime('%A, %B %d, %Y')
#                     formatted_date2 = date_obj.strftime('%B %d, %Y')
#                     return HttpResponse(f'<div id="date-display"><i class="fa fa-calendar"></i> {formatted_date}</div>\
#                                         <span id="target2" hx-swap-oob="true">{formatted_date2}</span>\
#                                         <button hx-swap-oob="true" type="submit" class="btn btn-success" id="target3"> \
#                                             <i class="fa fa-paper-plane"></i> Submit Booking Request\
#                                         </button>')
#                 except ValueError:
#                     return HttpResponse('<p>❌ Invalid date format</p>')
#             else:
#                 return HttpResponse('<p>No date selected</p>')
        
#         # Pre-fill customer details if user is authenticated
#         if request.user.is_authenticated:
#             initial_data.update({
#                 'customer_name': request.user.get_full_name() or request.user.username,
#                 'customer_email': request.user.email,
#                 'start_date': booking_params.get('event_date_str') if booking_params else None,
                
#             })
            
#             # Try to get phone from user profile if it exists
#             if hasattr(request.user, 'profile') and hasattr(request.user.profile, 'phone'):
#                 initial_data['customer_phone'] = request.user.profile.phone
        
#         form = BookingForm(initial=initial_data)
#         return render(request, 'events/booking_form.html', {
#             'form': form,
#             'event': event,
#             'selected_date': datetime.strptime(booking_params.get('event_date_str'), '%Y-%m-%d').date() if booking_params else None,
#         })

def booking_success(request, booking_id):
    """Display booking success page"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.user.is_authenticated and booking.customer != request.user:
        return redirect('home')  # or show error page
    
    if 'last_booking_id' in request.session:
        del request.session['last_booking_id']
    
    return render(request, 'events/booking_success.html', {
        'booking': booking,
        'event': booking.event
    })


@login_required
def booking_form(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    booking_params = request.session.get('booking_params')
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        event_date = datetime.strptime(booking_params.get('event_date_str'), '%Y-%m-%d').date() if booking_params else None
        
        if form.is_valid():
            if form.cleaned_data['start_date']:
                event_date = form.cleaned_data['start_date']
            try:
                is_available, message = check_event_availability(
                    event, 
                    event_date, 
                )
                
                if not is_available:
                    form.add_error(None, message)
                    
                    # Return the form with error message
                    context = {
                        'form': form,
                        'event': event,
                        'selected_date': event_date,
                        'message': message,
                    }
                    return render(request, 'events/booking_form.html', context)
                
                # Create the booking
                booking = form.save(commit=False)
                booking.customer = request.user if request.user.is_authenticated else None
                booking.event = event
                booking.start_date = event_date
                booking.end_date = event_date
                booking.status = 'pending'
                
                if request.user.is_authenticated:
                    booking.user = request.user
                
                booking.save()
                
                if 'booking_params' in request.session:
                    del request.session['booking_params']
                
                # Store booking ID in session for success page
                request.session['last_booking_id'] = booking.id
                success_url = reverse('booking_success', kwargs={'booking_id': booking.id})
                return redirect(success_url)
                
            except ValueError:
                form.add_error(None, 'Invalid date format')
        
        # If form is not valid, return form with errors
        else:
            print(form.errors)
            return render(request, 'events/booking_form.html', {
                'form': form,
                'event': event,
                'selected_date': event_date,
                'booking':booking
            })
    
    else:
        # GET request - show form with pre-filled data
        initial_data = {}

        if request.GET.get('start_date'):
            date_value = request.GET.get('start_date')
            
            if date_value:
                try:
                    start_date_availability = check_event_availability(event, datetime.strptime(date_value, '%Y-%m-%d').date())
                    if not start_date_availability[0]:
                        return HttpResponse(f'<div id="date-display"><i class="fa fa-calendar"></i>❌ {start_date_availability[1]}</div>\
                                                <span id="target2" hx-swap-oob="true">❌ {start_date_availability[1]}</span>\
                                                <button hx-swap-oob="true" type="submit" class="btn btn-success" id="target3" disabled>\
                                                    <i class="fa fa-paper-plane"></i> Submit Booking Request\
                                                </button>')
                    date_obj = datetime.strptime(date_value, '%Y-%m-%d')
                    formatted_date = date_obj.strftime('%A, %B %d, %Y')
                    formatted_date2 = date_obj.strftime('%B %d, %Y')
                    return HttpResponse(f'<div id="date-display"><i class="fa fa-calendar"></i> {formatted_date}</div>\
                                        <span id="target2" hx-swap-oob="true">{formatted_date2}</span>\
                                        <button hx-swap-oob="true" type="submit" class="btn btn-success" id="target3"> \
                                            <i class="fa fa-paper-plane"></i> Submit Booking Request\
                                        </button>')
                except ValueError:
                    return HttpResponse('<p>❌ Invalid date format</p>')
            else:
                return HttpResponse('<p>No date selected</p>')
        
        # Pre-fill customer details if user is authenticated
        if request.user.is_authenticated:
            initial_data.update({
                'customer_name': request.user.get_full_name() or request.user.username,
                'customer_email': request.user.email,
                'start_date': booking_params.get('event_date_str') if booking_params else None,
                
            })
            # Try to get phone from user profile if it exists
            if hasattr(request.user, 'profile') and hasattr(request.user.profile, 'mobile'):
                initial_data['customer_phone'] = request.user.profile.mobile
        
        form = BookingForm(initial=initial_data)
        return render(request, 'events/booking_form.html', {
            'form': form,
            'event': event,
            'selected_date': datetime.strptime(booking_params.get('event_date_str'), '%Y-%m-%d').date() if booking_params else None,
        })