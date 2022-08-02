from django.db import models
from django.contrib.auth.models import User


class Member(models.Model):
    name = models.CharField(max_length=30, null=False)
    email = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='images/', default='images/home-profile.jpg', null=True)
    def __str__(self):
        return self.name
