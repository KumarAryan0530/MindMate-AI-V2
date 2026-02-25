from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Quiz genre/subject tags
QUIZ_GENRES = [
    ('mental_health', 'Mental Health'),
    ('psychology', 'Psychology'),
    ('wellness', 'Wellness & Self-Care'),
    ('stress_management', 'Stress Management'),
    ('mindfulness', 'Mindfulness & Meditation'),
    ('cognitive', 'Cognitive Science'),
    ('emotional_intelligence', 'Emotional Intelligence'),
    ('general_knowledge', 'General Knowledge'),
]


class Quiz(models.Model):
    """Stores generated quiz data"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes')
    genre = models.CharField(max_length=50, choices=QUIZ_GENRES)
    questions_data = models.JSONField()  # Store all 20 questions with answers
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Quizzes'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_genre_display()} ({self.created_at.strftime('%Y-%m-%d')})"


class QuizAttempt(models.Model):
    """Stores user's quiz attempt and scores"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    genre = models.CharField(max_length=50, choices=QUIZ_GENRES)
    
    # Scoring
    total_questions = models.IntegerField(default=20)
    correct_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)
    skipped_answers = models.IntegerField(default=0)
    score = models.IntegerField(default=0)  # correct*2 + wrong*(-1) + skipped*0
    
    # Performance metrics
    time_taken = models.IntegerField(null=True, blank=True, help_text="Time in seconds")
    accuracy = models.FloatField(default=0.0)  # Percentage of correct answers
    
    # Detailed answers
    user_answers = models.JSONField(default=dict)  # Question index: user's answer
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_genre_display()} - Score: {self.score}"
    
    def calculate_score(self):
        """Calculate final score based on answers"""
        self.score = (self.correct_answers * 2) + (self.wrong_answers * -1)
        if self.total_questions > 0:
            self.accuracy = (self.correct_answers / self.total_questions) * 100
        self.save()
    
    def complete_quiz(self):
        """Mark quiz as completed"""
        self.is_completed = True
        self.completed_at = timezone.now()
        if self.started_at:
            self.time_taken = (self.completed_at - self.started_at).seconds
        self.calculate_score()


class QuizQuestion(models.Model):
    """Stores individual questions for tracking (optional, for analytics)"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    options = models.JSONField()  # List of 4 options
    correct_answer = models.CharField(max_length=500)
    difficulty = models.CharField(max_length=20, default='medium')
    question_number = models.IntegerField()
    
    class Meta:
        ordering = ['question_number']
    
    def __str__(self):
        return f"Q{self.question_number}: {self.question_text[:50]}..."


class Leaderboard(models.Model):
    """Aggregated leaderboard data for performance"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaderboard_entries')
    genre = models.CharField(max_length=50, choices=QUIZ_GENRES, null=True, blank=True)
    
    # Overall statistics
    total_attempts = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)
    highest_score = models.IntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    total_correct = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    overall_accuracy = models.FloatField(default=0.0)
    
    # Timestamps
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'genre']
        ordering = ['-total_score', '-average_score']
    
    def __str__(self):
        genre_display = self.get_genre_display() if self.genre else "Overall"
        return f"{self.user.username} - {genre_display} - Score: {self.total_score}"
    
    def update_stats(self):
        """Update leaderboard statistics based on user's attempts"""
        if self.genre:
            attempts = QuizAttempt.objects.filter(
                user=self.user, 
                genre=self.genre, 
                is_completed=True
            )
        else:
            attempts = QuizAttempt.objects.filter(
                user=self.user, 
                is_completed=True
            )
        
        self.total_attempts = attempts.count()
        if self.total_attempts > 0:
            self.total_score = sum(a.score for a in attempts)
            self.highest_score = max(a.score for a in attempts)
            self.average_score = self.total_score / self.total_attempts
            self.total_correct = sum(a.correct_answers for a in attempts)
            self.total_questions = sum(a.total_questions for a in attempts)
            if self.total_questions > 0:
                self.overall_accuracy = (self.total_correct / self.total_questions) * 100
        
        self.save()


class UsedQuestion(models.Model):
    """Track used questions to prevent duplicates"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='used_questions')
    genre = models.CharField(max_length=50, choices=QUIZ_GENRES)
    question_hash = models.CharField(max_length=64)  # Hash of question text
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'genre', 'question_hash']
        indexes = [
            models.Index(fields=['user', 'genre']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.genre} - Q:{self.question_hash[:8]}"
