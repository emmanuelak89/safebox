from django.urls import path,include
from django.conf.urls import url
from . import views
from django.conf import settings

urlpatterns = [
    path('viewfiles/', views.viewfiles, name='viewfiles'),
]