from django.db import models
from django.contrib.auth.models import User


class VoiceCallSchedule(models.Model):
    """Model for scheduling AI-powered wellness check-in calls"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='voice_call_schedules')
    phone_number = models.CharField(max_length=20)
    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # AI Agent Configuration
    custom_prompt = models.TextField(
        blank=True, 
        null=True,
        help_text="Custom focus for the AI conversation (e.g., 'stress management')"
    )
    first_message = models.TextField(
        blank=True, 
        null=True,
        help_text="Custom greeting message"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_time']
        verbose_name = 'Voice Call Schedule'
        verbose_name_plural = 'Voice Call Schedules'
        
    def __str__(self):
        return f"{self.user.username} - {self.scheduled_time.strftime('%Y-%m-%d %H:%M')}"


class VoiceCallHistory(models.Model):
    """Model for storing completed call details and transcripts"""
    
    schedule = models.ForeignKey(
        VoiceCallSchedule, 
        on_delete=models.CASCADE,
        related_name='call_histories'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='voice_call_histories')
    
    # Call Details
    twilio_call_sid = models.CharField(max_length=100, unique=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    call_started_at = models.DateTimeField(null=True, blank=True)
    call_ended_at = models.DateTimeField(null=True, blank=True)
    
    # Conversation Data
    user_transcript = models.TextField(
        blank=True,
        help_text="What the user said during the call"
    )
    agent_responses = models.TextField(
        blank=True,
        help_text="AI agent's responses"
    )
    full_transcript = models.JSONField(
        default=dict,
        blank=True,
        help_text="Complete conversation transcript with timestamps"
    )
    
    # Sentiment & Analysis
    overall_sentiment = models.CharField(
        max_length=20, 
        null=True, 
        blank=True,
        choices=[
            ('positive', 'Positive'),
            ('neutral', 'Neutral'),
            ('negative', 'Negative'),
        ]
    )
    emotional_score = models.FloatField(
        null=True, 
        blank=True,
        help_text="Overall emotional well-being score (0-25)"
    )
    stress_indicators = models.JSONField(
        default=list,
        blank=True,
        help_text="List of stress indicators detected"
    )
    
    # Call Status
    call_status = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Twilio call status"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Voice Call History'
        verbose_name_plural = 'Voice Call Histories'
        
    def __str__(self):
        return f"{self.user.username} - {self.call_started_at.strftime('%Y-%m-%d %H:%M') if self.call_started_at else 'N/A'}"
    
    @property
    def duration_formatted(self):
        """Return formatted call duration (e.g., '5m 30s')"""
        if self.duration_seconds:
            minutes = self.duration_seconds // 60
            seconds = self.duration_seconds % 60
            return f"{minutes}m {seconds}s"
        return "N/A"


class CallSentiment(models.Model):
    """Model for detailed sentiment analysis of voice calls"""
    
    call_history = models.OneToOneField(
        VoiceCallHistory, 
        on_delete=models.CASCADE,
        related_name='sentiment'
    )
    
    # Sentiment Scores (0-25 to match existing MindMate-AI system)
    positive_score = models.FloatField(default=0, help_text="Positive sentiment score")
    negative_score = models.FloatField(default=0, help_text="Negative sentiment score")
    neutral_score = models.FloatField(default=0, help_text="Neutral sentiment score")
    
    # Emotional States Detected
    emotions_detected = models.JSONField(
        default=list,
        blank=True,
        help_text="List of emotions detected (e.g., ['happy', 'anxious'])"
    )
    
    # Key phrases that indicate emotional state
    key_phrases = models.JSONField(
        default=list,
        blank=True,
        help_text="Important phrases that indicate mental health state"
    )
    
    # Integration with existing mental health score
    contributes_to_phq9 = models.BooleanField(
        default=True,
        help_text="Whether this call should contribute to PHQ-9 calculation"
    )
    mental_health_impact = models.FloatField(
        null=True, 
        blank=True,
        help_text="Impact on overall mental health score (-25 to +25)"
    )
    
    # Analysis metadata
    analyzed_at = models.DateTimeField(auto_now_add=True)
    analysis_confidence = models.FloatField(
        default=0.0,
        help_text="Confidence score of the sentiment analysis (0-1)"
    )
    
    class Meta:
        verbose_name = 'Call Sentiment Analysis'
        verbose_name_plural = 'Call Sentiment Analyses'
        
    def __str__(self):
        return f"Sentiment for {self.call_history.user.username} - {self.analyzed_at.strftime('%Y-%m-%d')}"
    
    @property
    def dominant_sentiment(self):
        """Return the dominant sentiment category"""
        scores = {
            'positive': self.positive_score,
            'negative': self.negative_score,
            'neutral': self.neutral_score
        }
        return max(scores.items(), key=lambda x: x[1])[0]
