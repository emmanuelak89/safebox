# Generated by Django 3.2.9 on 2022-04-20 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='image',
            field=models.ImageField(default='images/home-profile.jpg', null=True, upload_to='images/'),
        ),
    ]