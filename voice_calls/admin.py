from django.contrib import admin
from .models import VoiceCallSchedule, VoiceCallHistory, CallSentiment


@admin.register(VoiceCallSchedule)
class VoiceCallScheduleAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'scheduled_time', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Call Information', {
            'fields': ('user', 'phone_number', 'scheduled_time', 'status')
        }),
        ('AI Configuration', {
            'fields': ('custom_prompt', 'first_message'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VoiceCallHistory)
class VoiceCallHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'call_started_at', 'duration_formatted', 'overall_sentiment', 'call_status']
    list_filter = ['overall_sentiment', 'call_status', 'created_at']
    search_fields = ['user__username', 'twilio_call_sid']
    readonly_fields = ['created_at', 'updated_at', 'duration_formatted']
    
    fieldsets = (
        ('Call Details', {
            'fields': ('schedule', 'user', 'twilio_call_sid', 'call_started_at', 'call_ended_at', 'duration_seconds', 'duration_formatted', 'call_status')
        }),
        ('Conversation', {
            'fields': ('user_transcript', 'agent_responses', 'full_transcript'),
            'classes': ('collapse',)
        }),
        ('Analysis', {
            'fields': ('overall_sentiment', 'emotional_score', 'stress_indicators')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CallSentiment)
class CallSentimentAdmin(admin.ModelAdmin):
    list_display = ['call_history', 'dominant_sentiment', 'analysis_confidence', 'analyzed_at']
    list_filter = ['contributes_to_phq9', 'analyzed_at']
    readonly_fields = ['analyzed_at', 'dominant_sentiment']
    
    fieldsets = (
        ('Call Reference', {
            'fields': ('call_history',)
        }),
        ('Sentiment Scores', {
            'fields': ('positive_score', 'negative_score', 'neutral_score')
        }),
        ('Emotional Analysis', {
            'fields': ('emotions_detected', 'key_phrases')
        }),
        ('Mental Health Impact', {
            'fields': ('contributes_to_phq9', 'mental_health_impact', 'analysis_confidence')
        }),
        ('Metadata', {
            'fields': ('analyzed_at',)
        }),
    )
