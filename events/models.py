from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from PIL import Image
from datetime import date, timedelta
import os
from io import BytesIO
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
# Create your models here.

EVENTS = (
    ('Eventmanagement','Eventmanagement'),
    ('MakeupArtsist','Makeup Artsist'),
    ('Cakeshops','Cake shops'),
    ('MehandiArtist','Mehandi Artist'),
    ('Photographer','Photographer'),
    ('WeddingVenues','Wedding Venues'),
    ('CarsAndBuses','Cars and Buses'),
    ('InvitationCards','Invitation Cards'),
    ('Stagedecorator','Stage decorator'),
    ('CateringService','Catering Service'),
)


PLACES = (
    ('Thiruvananthapuram','Thiruvananthapuram'),
    ('Eranakulam','Eranakulam'),
    ('Thrissur','Thrissur'),
    ('Kollam','Kollam'),
    ('Palakkad','Palakkad'),
    ('Malappuram','Malappuram'),
    ('Kozhikode','Kozhikode'),
    ('Kottayam','Kottayam'),
    ('Alappuzha','Alappuzha'),
    ('Idukki','Idukki'),
    ('Pathanamthitta','Pathanamthitta'),
    ('Wayanad','Wayanad'),
    ('Kannur','Kannur'),
    ('Kasaragod','Kasaragod'),
)

class EventManager(models.Manager):
    def user_favourites(self,user):
        fav_list = []
        user_favourite = Event.objects.filter(favourites=user)
        for event in user_favourite:
            fav_list.append(event.id)
        return fav_list

class Facility(models.Model):
    """Model to store different types of facilities"""
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS class or icon name")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Facilities"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
class Event(models.Model):
    category = models.CharField(choices=EVENTS, max_length=20)
    name = models.CharField(max_length=100)
    place = models.CharField(choices=PLACES, max_length=100)
    mobile = models.CharField(max_length=20)
    address = models.TextField()
    price = models.DecimalField(max_digits=10,decimal_places=2)
    details = models.TextField(blank=True)
    favourites = models.ManyToManyField(User, blank=True, default=None, related_name="favourite")
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='events/',validators=[FileExtensionValidator(['jpeg','png', 'jpg'])], default='e_logo.jpg')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin')
    facilities = models.ManyToManyField(Facility, blank=True, related_name="events")
    
    objects = EventManager()

    def __str__(self):
        return {self.name}

    def get_facilities(self):
        """Get all active facilities for this event"""
        return self.facilities.filter(is_active=True)
    
    class Meta:
        ordering = ('-created',)

class BookingManager(models.Manager):
    def check_availability(self, event, start_date, end_date):
        available_list = []
        booking_list = Booking.objects.filter(event=event)
        for booking in booking_list:
            if booking.start_date > end_date or booking.end_date < start_date:
                available_list.append(True)
            else:
                available_list.append(False)
        return all(available_list)

    def get_all_dates(self,event):
        dates = []
        booked_list = Booking.objects.filter(event=event)
        for booking in booked_list:
            s_year = booking.start_date.year
            s_month = booking.start_date.month
            s_day = booking.start_date.day
            sdate = date(s_year, s_month, s_day)   # start date

            e_year = booking.end_date.year
            e_month = booking.end_date.month
            e_day = booking.end_date.day
            edate = date(e_year, e_month, e_day)   # end date

            delta = edate - sdate
            for i in range(delta.days + 1):
                day = sdate + timedelta(days=i)
                dates.append(day.strftime("%d/%m/%Y"))
        return set(dates)

class Booking(models.Model):
    BOOKING_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer')
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)  
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event')
    start_date = models.DateField(default=None)
    end_date = models.DateField(default=None)
    status = models.CharField(choices=BOOKING_STATUS, default='pending')
    updated = models.DateTimeField(auto_now=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    special_requirements = models.TextField(blank=True, null=True)

    objects = BookingManager()

    class Meta:
        ordering = ['-created']
    
    def save(self, *args, **kwargs):
        if not self.total_amount:
            self.total_amount = self.event.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer} -- {self.event} -- {self.status}"

ratings = (
    (1,'1'),
    (1.5,'1.5'),
    (2,'2'),
    (2.5,'2.5'),
    (3,'3'),
    (3.5,'3.5'),
    (4,'4'),
    (4.5,'4.5'),
    (5,'5'),
)

class ReviewManager(models.Manager):
    def average_ratings(self, event):
        average = []
        event = Review.objects.filter(event=event)
        for rating in event:
            average.append(rating.rating)
        total_ratings = len(average)
        avg_rating = 0
        if total_ratings != 0:
            for i in average:
                avg_rating += i
            event_rating = round(avg_rating/total_ratings,1)
        else:
            event_rating = 0
        return event_rating

    def user_review(self,event,user):
        users = []
        r = Review.objects.filter(event=event.id)
        for user in r:
            users.append(user.customer.id)
        return users


class Review(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='vendor')
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    rating = models.FloatField(choices=ratings)
    objects = ReviewManager()

    def __str__(self):
        return f'{self.customer}-{self.event.name}'

class EventGallery(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(
        upload_to='event_gallery/',
        validators=[FileExtensionValidator(['jpeg', 'png', 'jpg', 'webp'])]
    )
    title = models.CharField(max_length=200, blank=True, help_text="Optional title for the image")
    description = models.TextField(blank=True, help_text="Optional description of the work")
    is_featured = models.BooleanField(default=False, help_text="Mark as featured image")
    order = models.PositiveIntegerField(default=0, help_text="Display order (0 = first)")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    MAX_IMAGES_PER_EVENT = 10

    class Meta:
        ordering = ['order', '-uploaded_at']
        verbose_name = "Event Gallery Image"
        verbose_name_plural = "Event Gallery Images"

    def __str__(self):
        title = self.title if self.title else f"Image {self.id}"
        return f"{self.event.name} - {title}"
    
    def clean(self):
        """Validate image limits and featured image constraints"""
        super().clean()
        
        # Check image limit for new instances
        if not self.pk:  # New instance
            existing_count = EventGallery.objects.filter(event=self.event).count()
            if existing_count >= self.MAX_IMAGES_PER_EVENT:
                raise ValidationError(
                    f"Maximum {self.MAX_IMAGES_PER_EVENT} images allowed per event."
                )
        
        # Ensure only one featured image per event
        if self.is_featured:
            existing_featured = EventGallery.objects.filter(
                event=self.event, 
                is_featured=True
            ).exclude(pk=self.pk)
            
            if existing_featured.exists():
                existing_featured.update(is_featured=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if self.image:
            try:
                self._resize_image()
            except Exception as e:
                print(f"Image processing error: {e}")

    def _resize_image(self):
        """Resize image to optimize storage - works with both local and cloud storage"""
        try:
            # Check if we can access local path (for local storage)
            if hasattr(default_storage, 'path') and hasattr(self.image, 'path'):
                try:
                    # Try local storage approach first
                    img = Image.open(self.image.path)
                    if img.height > 800 or img.width > 800:
                        img.thumbnail((800, 800), Image.LANCZOS)
                        img.save(self.image.path, optimize=True, quality=85)
                    return
                except (NotImplementedError, AttributeError):
                    # Fall back to cloud storage approach
                    pass
            
            # Cloud storage approach
            # Open image from storage
            image_file = default_storage.open(self.image.name, 'rb')
            img = Image.open(image_file)
            image_file.close()
            
            # Check if resizing is needed
            if img.height > 800 or img.width > 800:
                # Create a copy for processing
                img_copy = img.copy()
                img_copy.thumbnail((800, 800), Image.LANCZOS)
                
                # Save to BytesIO
                temp_file = BytesIO()
                img_format = img_copy.format or 'JPEG'
                
                # Handle different image formats
                if img_format.upper() == 'PNG':
                    img_copy.save(temp_file, format='PNG', optimize=True)
                else:
                    # Convert to RGB if necessary (for JPEG)
                    if img_copy.mode in ('RGBA', 'LA', 'P'):
                        img_copy = img_copy.convert('RGB')
                    img_copy.save(temp_file, format='JPEG', optimize=True, quality=85)
                
                temp_file.seek(0)
                
                # Delete old file and save new one
                old_name = self.image.name
                default_storage.delete(old_name)
                
                # Save the processed image
                self.image.save(
                    old_name,
                    ContentFile(temp_file.read()),
                    save=False  # Don't trigger another save
                )
                temp_file.close()
                img_copy.close()
            
            img.close()
            
        except Exception as e:
            print(f"Error resizing image: {e}")

    def delete(self, *args, **kwargs):
        # Delete the image file when the model instance is deleted
        if self.image:
            try:
                # For both local and cloud storage
                if default_storage.exists(self.image.name):
                    default_storage.delete(self.image.name)
            except Exception as e:
                print(f"Error deleting image file: {e}")
        super().delete(*args, **kwargs)