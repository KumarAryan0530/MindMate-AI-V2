from django.contrib import admin
from .models import Quiz, QuizAttempt, QuizQuestion, Leaderboard, UsedQuestion, MiniGameScore, MiniGameLeaderboard


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['user', 'genre', 'created_at']
    list_filter = ['genre', 'created_at']
    search_fields = ['user__username']


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'genre', 'score', 'accuracy', 'is_completed', 'started_at']
    list_filter = ['genre', 'is_completed', 'started_at']
    search_fields = ['user__username']
    readonly_fields = ['started_at', 'completed_at']


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'question_number', 'difficulty']
    list_filter = ['difficulty']


@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ['user', 'genre', 'total_score', 'average_score', 'overall_accuracy', 'total_attempts']
    list_filter = ['genre']
    search_fields = ['user__username']
    readonly_fields = ['last_updated']


@admin.register(UsedQuestion)
class UsedQuestionAdmin(admin.ModelAdmin):
    list_display = ['user', 'genre', 'question_hash', 'created_at']
    list_filter = ['genre', 'created_at']
    search_fields = ['user__username']


@admin.register(MiniGameScore)
class MiniGameScoreAdmin(admin.ModelAdmin):
    list_display = ['user', 'game_type', 'difficulty', 'score', 'time_taken', 'moves_count', 'completed', 'created_at']
    list_filter = ['game_type', 'difficulty', 'completed', 'created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at']


@admin.register(MiniGameLeaderboard)
class MiniGameLeaderboardAdmin(admin.ModelAdmin):
    list_display = ['user', 'game_type', 'total_games', 'highest_score', 'average_score', 'best_time']
    list_filter = ['game_type']
    search_fields = ['user__username']
    readonly_fields = ['last_played']
