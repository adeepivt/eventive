from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from PIL import Image
# Create your models here.

EVENTS = (
    ('Cakeshops','Cakeshops'),
    ('CarsAndBuses','Cars and Buses'),
    ('CateringService','Catering Service'),
    ('Eventmanagement','Eventmanagement'),
    ('InvitationCards','Invitation Cards'),
    ('MakeupArtsist','Makeup Artsist'),
    ('MehandiArtist','Mehandi Artist'),
    ('Photographer','Photographer'),
    ('Stagedecorator','Stagedecorator'),
    ('WeddingVenues','Wedding Venues'),
)

class Event(models.Model):
    category = models.CharField(choices=EVENTS, max_length=20)
    name = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
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