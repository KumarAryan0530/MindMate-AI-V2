from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import VoiceCallSchedule, VoiceCallHistory
from .forms import ScheduleCallForm
import logging

logger = logging.getLogger(__name__)


@login_required
def schedule_call(request):
    """View to schedule a wellness call"""
    if request.method == 'POST':
        form = ScheduleCallForm(request.POST)
        if form.is_valid():
            # Check if user has phone number
            try:
                profile = request.user.profile
                if not profile.phone_number:
                    return JsonResponse({
                        'success': False,
                        'error': 'Please add your phone number in your profile first'
                    }, status=400)
                
                # Create call schedule
                call_schedule = form.save(commit=False)
                call_schedule.user = request.user
                call_schedule.phone_number = profile.phone_number
                call_schedule.save()
                
                logger.info(f"Call scheduled successfully for {request.user.username} at {call_schedule.scheduled_time}")
                
                return JsonResponse({
                    'success': True,
                    'message': 'Call scheduled successfully',
                    'call_id': call_schedule.id,
                    'scheduled_time': call_schedule.scheduled_time.strftime('%Y-%m-%d %H:%M')
                })
                
            except Exception as e:
                logger.error(f"Error scheduling call: {e}")
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=500)
        else:
            return JsonResponse({
                'success': False,
                'error': 'Please correct the errors in the form',
                'form_errors': form.errors
            }, status=400)
    else:
        form = ScheduleCallForm()
    
    # Get user's upcoming scheduled calls
    upcoming_calls = VoiceCallSchedule.objects.filter(
        user=request.user,
        status__in=['pending', 'in_progress']
    ).order_by('scheduled_time')[:5]
    
    context = {
        'form': form,
        'upcoming_calls': upcoming_calls
    }
    return render(request, 'voice_calls/schedule.html', context)


@csrf_exempt
def twilio_twiml(request, schedule_id):
    """Generate TwiML for Twilio call"""
    try:
        schedule = VoiceCallSchedule.objects.get(id=schedule_id)
        
        # Get WebSocket stream URL
        if settings.NGROK_URL:
            host = settings.NGROK_URL.replace('https://', '').replace('http://', '')
            stream_url = f"wss://{host}/ws/media-stream/{schedule_id}/"
        else:
            # Fallback for local development
            host = request.get_host()
            stream_url = f"wss://{host}/ws/media-stream/{schedule_id}/"
        
        # Default prompt and message
        prompt = schedule.custom_prompt or """
        You are MindMate AI, a compassionate mental health wellness assistant.
        Your role is to check in on the user's emotional well-being, listen empathetically,
        and guide them through a brief breathing exercise if they're feeling stressed.
        Be warm, patient, and supportive. Keep responses concise and natural.
        """
        
        first_message = schedule.first_message or (
            "Hi! I'm calling from MindMate AI for your scheduled wellness check-in. "
            "How are you feeling today?"
        )
        
        # Escape XML special characters for TwiML
        def escape_xml(text):
            return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')
        
        prompt = escape_xml(prompt)
        first_message = escape_xml(first_message)
        stream_url = escape_xml(stream_url)
        
        # Generate TwiML with Connect for bidirectional streaming
        # Note: Trial accounts will play a message BEFORE this TwiML executes
        # The message says "press any key" and when user presses, this TwiML runs
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="{stream_url}">
            <Parameter name="prompt" value="{prompt}" />
            <Parameter name="first_message" value="{first_message}" />
        </Stream>
    </Connect>
</Response>'''
        
        logger.info(f"TwiML generated for schedule {schedule_id} with stream URL: {stream_url}")
        return HttpResponse(twiml, content_type='text/xml')
    
    except VoiceCallSchedule.DoesNotExist:
        logger.error(f"Call schedule {schedule_id} not found")
        error_twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Aditi" language="en-IN">Sorry, we could not find your call schedule. Please contact support.</Say>
    <Hangup/>
</Response>'''
        return HttpResponse(error_twiml, content_type='text/xml', status=404)
    except Exception as e:
        logger.error(f"Error generating TwiML: {e}")
        error_twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Aditi" language="en-IN">Sorry, an error occurred. Please try again later.</Say>
    <Hangup/>
</Response>'''
        return HttpResponse(error_twiml, content_type='text/xml', status=500)


@login_required
def call_history(request):
    """View call history"""
    calls = VoiceCallHistory.objects.filter(user=request.user).select_related('schedule')
    
    context = {
        'calls': calls
    }
    return render(request, 'voice_calls/history.html', context)


@login_required
def call_detail(request, call_id):
    """View detailed information about a specific call"""
    call = get_object_or_404(
        VoiceCallHistory.objects.select_related('schedule'),
        id=call_id,
        user=request.user
    )
    
    context = {
        'call': call
    }
    return render(request, 'voice_calls/call_detail.html', context)


@login_required
@require_POST
def cancel_call(request, schedule_id):
    """Cancel a scheduled call"""
    try:
        schedule = VoiceCallSchedule.objects.get(
            id=schedule_id,
            user=request.user,
            status='pending'
        )
        
        schedule.status = 'cancelled'
        schedule.save()
        
        logger.info(f"Call {schedule_id} cancelled by user {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'message': 'Call cancelled successfully'
        })
    
    except VoiceCallSchedule.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Call not found or already completed'
        }, status=404)
