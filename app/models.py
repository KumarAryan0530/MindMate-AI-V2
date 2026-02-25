from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class TestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phq9_score = models.IntegerField()
    total_score = models.IntegerField(null=True, blank=True)
    Status = models.CharField(max_length=100, null=True, blank=True)
    emotions = models.JSONField(null=True, blank=True)
    emotion_score = models.IntegerField(null=True, blank=True)
    audio_sentiment = models.JSONField(null=True, blank=True)  # New field
    audio_duration = models.FloatField(null=True, blank=True)  # New field
    audio_analysis = models.JSONField(default=dict)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.phq9_score}"


# Temproary model for storing session data

class EmotionSessionData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    emotion_score = models.IntegerField(default=0)
    emotion_counts = models.JSONField(default=dict)  # Storing emotion counts as JSON
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Emotion data for {self.user}"





class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    


class JournalEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    entry_date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    positive_score = models.FloatField(default=0)
    negative_score = models.FloatField(default=0)

    class Meta:
        ordering = ['-entry_date']


class Prescription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prescription_image = models.ImageField(upload_to='prescriptions/', null=True, blank=True)
    prescription_file = models.FileField(upload_to='prescriptions/', null=True, blank=True)  # For PDF support
    extracted_data = models.JSONField(default=dict)  # Store structured extracted data
    extracted_text = models.TextField(blank=True)  # Store HTML formatted text
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Prescription for {self.user.username} - {self.created_at.strftime('%Y-%m-%d')}"