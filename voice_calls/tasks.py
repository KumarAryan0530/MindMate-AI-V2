from celery import shared_task
from django.utils import timezone
from django.conf import settings
from .models import VoiceCallSchedule, VoiceCallHistory, CallSentiment
from .services.twilio_service import TwilioService
from .services.elevenlabs_service import ElevenLabsService
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_scheduled_calls():
    """Check for pending calls that need to be made"""
    from datetime import timedelta
    
    now = timezone.now()
    # Add 30 second buffer to catch calls scheduled for "now"
    check_time = now + timedelta(seconds=30)
    
    pending_calls = VoiceCallSchedule.objects.filter(
        status='pending',
        scheduled_time__lte=check_time
    )
    
    count = pending_calls.count()
    if count > 0:
        logger.info(f"Found {count} pending call(s) to initiate at {now}")
        
        for call_schedule in pending_calls:
            try:
                logger.info(f"Initiating call for schedule ID: {call_schedule.id} (scheduled for {call_schedule.scheduled_time})")
                initiate_call.delay(call_schedule.id)
            except Exception as e:
                logger.error(f"Failed to queue call {call_schedule.id}: {e}")
    
    return f"Checked {count} pending calls"


@shared_task
def initiate_call(schedule_id):
    """Initiate a Twilio call"""
    try:
        call_schedule = VoiceCallSchedule.objects.get(id=schedule_id)
        
        if call_schedule.status != 'pending':
            logger.warning(f"Call {schedule_id} is not pending (status: {call_schedule.status})")
            return f"Call not pending: {call_schedule.status}"
        
        # Update status
        call_schedule.status = 'in_progress'
        call_schedule.save()
        
        # Create TwiML URL
        if settings.NGROK_URL:
            base_url = settings.NGROK_URL
        else:
            base_url = "http://localhost:8000"  # Fallback for local dev
        
        twiml_url = f"{base_url}/voice/twiml/{schedule_id}/"
        
        # Initiate call via Twilio
        service = TwilioService()
        call_sid = service.initiate_call(
            to_number=call_schedule.phone_number,
            twiml_url=twiml_url
        )
        
        # Create call history record
        VoiceCallHistory.objects.create(
            schedule=call_schedule,
            user=call_schedule.user,
            twilio_call_sid=call_sid,
            call_started_at=timezone.now()
        )
        
        logger.info(f"Call initiated successfully: {call_sid} for schedule {schedule_id}")
        
        # Schedule status update check
        update_call_status.apply_async(args=[call_sid], countdown=300)  # Check after 5 minutes
        
        return f"Call initiated: {call_sid}"
        
    except VoiceCallSchedule.DoesNotExist:
        logger.error(f"Call schedule {schedule_id} not found")
        return f"Schedule not found: {schedule_id}"
    except Exception as e:
        logger.error(f"Failed to initiate call for schedule {schedule_id}: {e}")
        
        # Update schedule status to failed
        try:
            call_schedule = VoiceCallSchedule.objects.get(id=schedule_id)
            call_schedule.status = 'failed'
            call_schedule.save()
        except Exception:
            pass
        
        return f"Failed to initiate call: {e}"


@shared_task
def update_call_status(call_sid):
    """Update call status from Twilio"""
    try:
        call_history = VoiceCallHistory.objects.get(twilio_call_sid=call_sid)
        
        service = TwilioService()
        details = service.get_call_details(call_sid)
        
        if details:
            call_history.duration_seconds = details['duration']
            call_history.call_ended_at = details['end_time']
            call_history.call_status = details['status']
            call_history.save()
            
            # Update schedule status
            schedule = call_history.schedule
            if details['status'] in ['completed', 'busy', 'no-answer', 'failed', 'canceled']:
                schedule.status = 'completed' if details['status'] == 'completed' else 'failed'
                schedule.save()
            
            logger.info(f"Call status updated: {call_sid} - {details['status']}")
            
            # Analyze sentiment if call completed
            if details['status'] == 'completed' and call_history.user_transcript:
                analyze_call_sentiment.delay(call_history.id)
        
        return f"Status updated for {call_sid}"
    
    except VoiceCallHistory.DoesNotExist:
        logger.error(f"Call history not found for SID: {call_sid}")
        return f"Call history not found: {call_sid}"
    except Exception as e:
        logger.error(f"Failed to update call status for {call_sid}: {e}")
        return f"Failed to update status: {e}"


@shared_task
def analyze_call_sentiment(call_history_id):
    """Analyze sentiment of a completed call"""
    try:
        call_history = VoiceCallHistory.objects.get(id=call_history_id)
        
        # Combine user transcript and agent responses
        full_text = f"{call_history.user_transcript} {call_history.agent_responses}"
        
        if not full_text.strip():
            logger.warning(f"No transcript available for call {call_history_id}")
            return "No transcript to analyze"
        
        # Analyze sentiment using ElevenLabs service
        service = ElevenLabsService()
        sentiment_data = service.analyze_sentiment(full_text)
        
        # Create or update sentiment record
        sentiment, created = CallSentiment.objects.update_or_create(
            call_history=call_history,
            defaults={
                'positive_score': sentiment_data.get('positive_score', 0),
                'negative_score': sentiment_data.get('negative_score', 0),
                'neutral_score': sentiment_data.get('neutral_score', 0),
                'emotions_detected': sentiment_data.get('emotions_detected', []),
                'key_phrases': sentiment_data.get('key_phrases', []),
                'analysis_confidence': sentiment_data.get('confidence', 0.0),
                'mental_health_impact': calculate_mental_health_impact(sentiment_data)
            }
        )
        
        # Update call history overall sentiment
        call_history.overall_sentiment = sentiment_data.get('sentiment', 'neutral')
        call_history.emotional_score = sentiment_data.get('positive_score', 0)
        call_history.save()
        
        action = "Created" if created else "Updated"
        logger.info(f"{action} sentiment analysis for call {call_history_id}")
        
        return f"Sentiment analyzed for call {call_history_id}"
    
    except VoiceCallHistory.DoesNotExist:
        logger.error(f"Call history {call_history_id} not found")
        return f"Call not found: {call_history_id}"
    except Exception as e:
        logger.error(f"Failed to analyze sentiment for call {call_history_id}: {e}")
        return f"Failed to analyze sentiment: {e}"


def calculate_mental_health_impact(sentiment_data):
    """Calculate mental health impact score from sentiment data"""
    positive = sentiment_data.get('positive_score', 0)
    negative = sentiment_data.get('negative_score', 0)
    
    # Calculate impact (-25 to +25 scale)
    impact = (positive - negative)
    
    # Clamp to valid range
    return max(-25, min(25, impact))
