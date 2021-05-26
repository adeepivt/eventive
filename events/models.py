from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from PIL import Image
from datetime import date, timedelta
# Create your models here.

EVENTS = (
    ('Eventmanagement','Eventmanagement'),
    ('MakeupArtsist','Makeup Artsist'),
    ('MehandiArtist','Mehandi Artist'),
    ('Photographer','Photographer'),
    ('WeddingVenues','Wedding Venues'),
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

    def __str__(self):
        return f"Eventive-{self.user} - {self.category} - {self.price}"


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
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event')
    start_date = models.DateField(default=None)
    end_date = models.DateField(default=None)
    status = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = BookingManager()

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
                print(i)
                avg_rating += i
            event_rating = avg_rating/total_ratings
        else:
            event_rating = 0
        return event_rating


class Review(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='vendor')
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(choices=ratings)
    objects = ReviewManager()

    def __str__(self):
        return f'{self.customer}-{self.event.name}'

