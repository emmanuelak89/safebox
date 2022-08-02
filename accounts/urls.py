from django.urls import path,include
from django.conf.urls import url
from . import views
from django.conf import settings
from rest_framework.routers import DefaultRouter

router = DefaultRouter()


urlpatterns = [
    path('router/', include(router.urls)),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
#url(r'^google-login/$', views.google_login, name="google_login"),
    url('google-login/', views.google_login, name='google_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('community/', views.community, name='community'),
    path('search/', views.search, name='search'),
    path('filter/<str:category>', views.filter, name='filter'),
    path('editprofile/', views.editprofile, name='editprofile'),
    path('newfile/', views.uploadfile, name='newfile'),
    path('changetype/<str:id>', views.changetype, name='changetype'),
    path('delete/<str:id>', views.deletefile, name='delete'),
    path('download/<str:id>', views.download, name='download'),
    path('memberz/', views.member_list),
    path('memberupdate/<int:id>/', views.mygeneric.as_view()),
    path('memberdetail/<int:pk>', views.member_detail),
]