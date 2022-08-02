from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class File(models.Model):
    name = models.CharField(max_length=50)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default='ADMIN')
    filetype = models.CharField(max_length=10, null=False, default='private')
    category = models.CharField(max_length=25, null=False, default='music')
    description = models.CharField(max_length=100,null=True,default='no description')
    uploaded_date = models.DateTimeField(default=datetime.now, blank=True)
    downloaded = models.IntegerField(default=0)

class FileRepo(models.Model):
    document_name = models.CharField(max_length=100)
    document_src = models.FileField(upload_to='file/', blank=True, null=True)
    file = models.ForeignKey(File, on_delete=models.CASCADE, null=True, default=1)