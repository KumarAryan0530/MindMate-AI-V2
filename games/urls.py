from django.urls import path
from . import views

app_name = 'games'

urlpatterns = [
    path('', views.games_home, name='home'),
    path('quiz/select-genre/', views.select_genre, name='select_genre'),
    path('quiz/generate/', views.generate_quiz, name='generate_quiz'),
    path('quiz/take/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('quiz/submit-answer/', views.submit_answer, name='submit_answer'),
    path('quiz/complete/<int:attempt_id>/', views.complete_quiz, name='complete_quiz'),
    path('quiz/results/<int:attempt_id>/', views.quiz_results, name='quiz_results'),
    path('analytics/', views.analytics_dashboard, name='analytics'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('continue-quiz/', views.continue_quiz, name='continue_quiz'),
]
