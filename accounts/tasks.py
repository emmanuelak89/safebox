from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from repo.models import File,FileRepo
import zipfile

@shared_task(bind=True)
def test_func(self):
    for i in range(0,10):
        print(i)
    return 'done'

@shared_task(bind=True)
def send_email(self):
        emailto = 'oladipupoemmanuel85@gmail.com'
        subject = 'Weekly Newsletter'
        message = f'This week is the *perfect* time to browse through the most shared files on our platform.\n From now until the end of the week, you can take download an unlimited amount of files completely free.'
        email_from = settings.EMAIL_HOST_USER
        recipient = [emailto,]
        send_mail(subject,message,email_from,recipient)

@shared_task(bind=True)
def downloadfiles(self,id):
    filename = 'Safebox_download.zip'
    response = HttpResponse(content_type='application/zip')
    zf = zipfile.ZipFile(response, 'w')
    file = File.objects.get(id=id)
    documents = FileRepo.objects.filter(file=file)
    for document in documents:
        zf.write('./media/' + str(document.document_src))
    response['Content-Disposition'] = f'attachment; filename={filename}'
    file.downloaded += 1
    file.save()
    return response