from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import auth
import django_rq
from .models import Member
import requests
from django.urls import reverse
from datetime import datetime
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status,viewsets
from rest_framework import generics
from rest_framework import mixins
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import  IsAuthenticated
from rest_framework.views import APIView
from .serializers import MemberSerializer
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from .tasks import downloadfiles
from repo.models import File,FileRepo
from django.views.decorators.cache import cache_page
import zipfile


def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        name = request.POST['name']
        image = request.FILES['image']
        fs = FileSystemStorage()
        doc = fs.save(image.name, image)
        if request.POST['password'] == request.POST['password2']:
            user = User.objects.create_user(username=name, email=email, password=password)
            user.save()
            member = Member(name=name,email=user,image=doc)
            member.save()
            auth.login(request, user)
            return redirect('dashboard')
        else:
            mg = 'passwords must match'
            return render(request, 'signup.html', {'mg': mg})
    else:
        return render(request, 'signup.html')

def signin(request):
    if request.method == 'POST':
        user = auth.authenticate(username=request.POST['email'], password=request.POST['password'])
        if user is not None:
            auth.login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'signin.html', {'mg': 'username or password is incorrect'})
    else:
        return render(request, 'signin.html')

def signout(request):
    auth.logout(request)
    return redirect('home')

def google_login(request):
    redirect_uri = "%s://%s%s" % (
        request.scheme, request.get_host(), reverse('google_login')
    )
    if('code' in request.GET):
        params = {
            'grant_type': 'authorization_code',
            'code': request.GET.get('code'),
            'redirect_uri': redirect_uri,
            'client_id': settings.GP_CLIENT_ID,
            'client_secret': settings.GP_CLIENT_SECRET
        }
        url = 'https://accounts.google.com/o/oauth2/token'
        response = requests.post(url, data=params)
        url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        access_token = response.json().get('access_token')
        response = requests.get(url, params={'access_token': access_token})
        user_data = response.json()
        email = user_data.get('email')
        if email:
            user, _ = User.objects.get_or_create(email=email, username=email,password=str(email)+'1234')
            gender = user_data.get('gender', '').lower()
            if gender == 'male':
                gender = 'M'
            elif gender == 'female':
                gender = 'F'
            else:
                gender = 'O'
            data = {
                'first_name': user_data.get('name', '').split()[0],
                'last_name': user_data.get('family_name'),
                'google_avatar': user_data.get('picture'),
                'gender': gender,
                'is_active': True
            }
            user.__dict__.update(data)
            user.save()
            user.backend = settings.AUTHENTICATION_BACKENDS[0]
            auth.login(request, user)
        else:
            messages.error(
                request,
                'Unable to login with Gmail Please try again'
            )
        return redirect('community')
    else:
        url = "https://accounts.google.com/o/oauth2/auth?client_id=%s&response_type=code&scope=%s&redirect_uri=%s&state=google"
        scope = [
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email"
        ]
        scope = " ".join(scope)
        url = url % (settings.GP_CLIENT_ID, scope, redirect_uri)
        return redirect(url)

@cache_page(60 * 2)
def dashboard(request):
    user = User.objects.get(username=request.user.get_username())
    uploaded = File.objects.filter(uploaded_by=user)
    try:
        recentlydownloaded = File.objects.filter(pk__in=request.session['recently_viewed'])
    except KeyError:
        recentlydownloaded = {}
    topdownloaded = File.objects.filter(uploaded_by=user).order_by('-downloaded')
    return render(request, 'dashboard.html', {'uploaded': uploaded , 'topdownloaded':topdownloaded, 'recentlydownloaded':recentlydownloaded})


def uploadfile(request):
    user = User.objects.get(username=request.user.get_username())
    filename = request.POST['file_name']
    filetype = request.POST['file_type']
    file = File(uploaded_by=user, name=filename,filetype =filetype )
    file.save()
    document_name = request.POST['document_name']
    document_src = request.FILES['document_src']
    fs = FileSystemStorage()
    doc = fs.save(document_src.name, document_src)
    user = User.objects.get(username=request.user.get_username())
    file = File.objects.get(uploaded_by=user, name=filename)
    document = FileRepo(file=file, document_name=document_name, document_src=doc)
    document.save()
    return redirect('dashboard')

@cache_page(60 * 1)
def search(request):
    filename = request.POST['search']
    files = File.objects.filter(name=filename)
    if files.count() > 0:
        mg = 'search successful, returned ' + str(files.count()) + ' file(s)'
        return render(request, 'search.html', {'files': files,'filename':filename, 'mg':mg})
    else:
        mg = 'search unsuccessful, no files found'
        return render(request,'search.html', {'mg':mg,'filename':filename})


@cache_page(60 * 1)
def community(request):
    folders = File.objects.all().order_by('-uploaded_date')
    topdownloaded = File.objects.all().order_by('-downloaded')
    return render(request,'community.html',{'folders':folders, 'topdownloaded':topdownloaded})

def filter(request,category):
    folders = File.objects.filter(category=category)
    return render(request, 'community.html', {'folders': folders})

def changetype(request,id):
    file = File.objects.get(id=id)
    if file.filetype == 'public':
        file.filetype = 'private'
        file.save()
    elif file.filetype == 'private':
        file.filetype = 'public'
        file.save()
    return redirect('dashboard')

def deletefile(request,id):
    file = File.objects.get(id=id)
    file.delete()
    return redirect('dashboard')

def editprofile(request):
    if request.method == 'POST':
        request.user.email=request.POST['email']
        request.user.save()
        request.user.set_password(request.POST['password'])
        request.user.save()
        return redirect('signin')
    else:
        return render(request, 'editprofile.html')


#Windows doesnt support fork()....likely to return module 'os' has no attribute 'fork'
# def downloadfile(request,id):
#     queue = django_rq.get_queue('default', default_timeout=800)
#     queue.enqueue(downloadfiles, args=(id,))

def download(request,id):
    filename = 'Safebox_download.zip'
    response = HttpResponse(content_type='application/zip')
    zf = zipfile.ZipFile(response, 'w')
    file = File.objects.get(id=id)
    if 'recently_viewed' in request.session:
        if id in request.session['recently_viewed']:
            request.session['recently_viewed'].remove(id)
        request.session['recently_viewed'].insert(0, id)
        if len(request.session['recently_viewed']) > 5:
            request.session['recently_viewed'].pop()
    else:
        request.session['recently_viewed'] = [id]
    request.session.modified = True
    documents = FileRepo.objects.filter(file=file)
    for document in documents:
        zf.write('./media/' + str(document.document_src))
    response['Content-Disposition'] = f'attachment; filename={filename}'
    file.downloaded += 1
    file.save()
    return response

# Basic function API to get all users and add a user
@api_view(['GET','POST'])
def member_list(request):
    if request.method == 'GET':
        members = Member.objects.all()
        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = MemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Basic function API to get a particular user, update user's details or delete the user
@api_view(['GET','PUT', 'DELETE'])
def member_detail(request,pk):
    try:
        member = Member.objects.get(pk=pk)

    except Member.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = MemberSerializer(member)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = MemberSerializer(member,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        member.delete()
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)

#APIView API to get all members and add a member
class MemberAPIView(APIView):
    def get(self,request):
        members = Member.objects.all()
        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data)

    def post(self,request):
        serializer = MemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# APIView API to get a particular member, update member's details or delete the member
class EditMemberAPIView(APIView):
    def get(self, request,pk):
        try:
            member = Member.objects.get(pk=pk)
        except Member.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        serializer = MemberSerializer(member)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self,request,pk):
        try:
            member = Member.objects.get(pk=pk)
        except Member.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        serializer = MemberSerializer(member, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,pk):
        try:
            member = Member.objects.get(pk=pk)
        except Member.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        member.delete()
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)

#APIView API to download files
class DownloadAPI(APIView):
    def get(self, request,id):
        try:
            file = File.objects.get(id=id)

        except File.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        filename = 'Safebox_download.zip'
        response = HttpResponse(content_type='application/zip')
        zf = zipfile.ZipFile(response, 'w')
        documents = FileRepo.objects.filter(file=file)
        for document in documents:
            zf.write('./media/' + str(document.document_src))
        response['Content-Disposition'] = f'attachment; filename={filename}'
        file.downloaded += 1
        file.save()
        return response


class mygeneric(generics.GenericAPIView,mixins.CreateModelMixin, mixins.UpdateModelMixin,mixins.ListModelMixin,mixins.DestroyModelMixin,mixins.RetrieveModelMixin):
    serializer_class = MemberSerializer
    queryset = Member.objects.all()
    lookup_field = 'id'
    authentication_classes = [SessionAuthentication,BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request, id=None):
        if id:
            return self.retrieve(request,id)
        else:
            return self.list(request)

    def post(self,request):
        return self.create(request)

    def put(self,request, id=None):
        return self.update(request,id)


    def delete(self,request, id=None):
        return self.destroy(request,id)

#New member API
class MemberAPI(generics.ListCreateAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

#Update Member details API
class MemberdetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
