import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsPaper.settings')

app = Celery('NewsPaper')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_connection_retry_on_startup = True
# app.autodiscover_tasks()
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    'send_weekly_newsletter': {
        'task': 'news.tasks.send_weekly_newsletter',
        'schedule': crontab(hour='8', minute='0', day_of_week='1'),
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')