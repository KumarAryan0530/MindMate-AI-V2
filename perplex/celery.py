"""
Celery configuration for SafeMind-AI
"""
import os
from celery import Celery

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'perplex.settings')

app = Celery('perplex')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()

# Periodic task schedule
app.conf.beat_schedule = {
    'check-scheduled-calls-every-minute': {
        'task': 'voice_calls.tasks.check_scheduled_calls',
        'schedule': 60.0,  # Run every 60 seconds
    },
}

@app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery configuration"""
    print(f'Request: {self.request!r}')
