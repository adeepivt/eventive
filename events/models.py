from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from PIL import Image
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
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='events/',validators=[FileExtensionValidator(['jpeg','png', 'jpg'])], default='e_logo.jpg')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin')

    def __str__(self):
        return f"Eventive-{self.user} - {self.category} - {self.price}"


    class Meta:
        ordering = ('-created',)

class Booking(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event')
    start_date = models.DateField(default=None)
    end_date = models.DateField(default=None, blank=True)
    status = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self):
        # self.first_char for referencing to the current object
        self.end_date = self.start_date
        super().save(self)

    def __str__(self):
        return f"{self.customer} -- {self.event} -- {self.status}"
