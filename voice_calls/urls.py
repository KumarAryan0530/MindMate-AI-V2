from django.urls import path
from . import views

app_name = 'voice_calls'

urlpatterns = [
    path('schedule/', views.schedule_call, name='schedule'),
    path('history/', views.call_history, name='history'),
    path('call/<int:call_id>/', views.call_detail, name='call_detail'),
    path('cancel/<int:schedule_id>/', views.cancel_call, name='cancel'),
    path('twiml/<int:schedule_id>/', views.twilio_twiml, name='twiml'),
]
