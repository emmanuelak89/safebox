from django.test import TestCase,Client,RequestFactory
from django.contrib.auth.models import User
from django.urls import resolve,reverse
from accounts.views import signin,signout,google_login
from accounts.models import Member

class TestUrl(TestCase):
    def test_if_signin_url_is_resolved(self):
        url = reverse('signin')
        myclient = Client()
        user = User.objects.create_user(username='opeoluwa@gmail.com', password='akerele')
        user.save()
        member = Member(email=user, name='ope')
        member.save()
        response = myclient.post(reverse('signin'), {'email': 'opeoluwa@gmail.com', 'password': 'akerele'})
        self.assertEquals(resolve(url).func, signin)
        self.assertEquals(response.status_code, 302)


    def test_if_signout_url_is_resolved(self):
        url = reverse('signout')
        myclient = Client()
        response = myclient.get('/accounts/signout/')
        self.assertEquals(resolve(url).func, signout)
        self.assertRedirects(response,'/',302,200)


    def test_if_google_login_url_is_resolved(self):
        url = reverse('google_login')
        self.assertEquals(resolve(url).func, google_login)

    def test_dashboard_url(self):
        myclient = Client()
        factory = RequestFactory()
        user = User.objects.create_user(username='opeoluwa1@gmail.com', password='akerele')
        user.save()
        member = Member(email=user, name='ope1')
        member.save()
        myclient.login(username='opeoluwa1@gmail.com', password='akerele')
        response = factory.post('/accounts/signin', {'username':'opeoluwa1@gmail.com', 'password':'akerele'})
        self.assertRedirects(response, '/accounts/dashboard', 302, 200)
        self.assertTemplateUsed(response, 'dashboard.html')

    # def test_uploadfile_url(self):
    #     myclient = Client()
    #     user = User.objects.create_user(username='opeoluwa2@gmail.com', password='akerele')
    #     factory = RequestFactory()
    #     myclient.login(username='opeoluwa2@gmail.com', password='akerele')
    #     myfile = open('media/AKERELE OLADIPUPO BIRTH CERTIFICATE.pdf','r')
    #     response = factory.post('dashboard',{'filename':'testfile','filetype':'private','document_name':'doc1','document_src':myfile})
    #     response.user = user
    #     if self.assertEquals(response.status_code, 200):
    #         self.assertRedirects(response, 'dashboard', 302, 200)
    #     else:
    #         print('error')
    #     user.delete()




