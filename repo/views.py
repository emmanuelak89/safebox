from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import File,FileRepo

def viewfiles(request):
    files = File.objects.filter(filetype='public')
    return render(request, 'viewfiles.html', {'files': files})

