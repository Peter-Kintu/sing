# project/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sing.settings')

app = Celery('sing')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()