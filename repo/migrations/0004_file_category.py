# Generated by Django 3.2.9 on 2022-04-19 23:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repo', '0003_auto_20220418_1539'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='category',
            field=models.CharField(default='music', max_length=25),
        ),
    ]