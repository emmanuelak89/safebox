from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safebox.settings')
app = Celery('safebox')
app.conf.enable_utc = False
app.conf.update(timezone = 'UTC')
app.autodiscover_tasks()
app.config_from_object(settings,namespace='CELERY')

# CELERY BEAT SETTINGS
app.conf.beat_schedule = {
    'send weekly newsletter':{
        'task' : 'accounts.tasks.send_email',
        'schedule': crontab(day_of_week=1,hour=0, minute=46)
    }
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
