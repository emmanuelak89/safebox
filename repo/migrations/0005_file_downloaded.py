# Generated by Django 3.2.9 on 2022-04-20 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repo', '0004_file_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='downloaded',
            field=models.IntegerField(default=0),
        ),
    ]
