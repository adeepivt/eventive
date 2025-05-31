from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django_resized import ResizedImageField
import uuid
# Create your models here.

USER_TYPE_CHOICES = [
    ('user', 'Regular User'),
    ('vendor', 'Vendor'),
]

APPROVAL_STATUS_CHOICES = [
    ('pending', 'Pending Approval'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('not_applicable', 'Not Applicable'), # For regular users
]
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=30, blank=True, null=True)
    mobile = models.CharField(max_length=20, null=True)
    is_admin = models.BooleanField(default=False)
    img = ResizedImageField(size=[300,300],quality=85,default='profile_pics/e_logo.jpg', upload_to='profile_pics')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='user')
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='not_applicable')


    def __str__(self):
        return self.user.username

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     image = Image.open(self.img.path)
    #     if image.height>300 and image.width>300:
    #         output_size = (300,300)
    #         image.thumbnail(output_size)
    #         image.save(self.img.path)

class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reset_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_when = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password reset for {self.user.username} at {self.created_when}"