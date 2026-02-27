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
    
    # Mini Games URLs
    path('mini-games/', views.mini_games_home, name='mini_games_home'),
    path('mini-games/memory-match/', views.memory_match_game, name='memory_match'),
    path('mini-games/pattern-recognition/', views.pattern_recognition_game, name='pattern_recognition'),
    path('mini-games/logic-puzzle/', views.logic_puzzle_game, name='logic_puzzle'),
    path('mini-games/ai-riddle/', views.ai_riddle_game, name='ai_riddle'),
    path('mini-games/save-score/', views.save_minigame_score, name='save_minigame_score'),
    path('mini-games/leaderboard/', views.minigame_leaderboard, name='minigame_leaderboard'),
    
    # AI-Powered Features
    path('mini-games/ai-hint/', views.get_ai_hint, name='get_ai_hint'),
    path('mini-games/generate-riddle/', views.generate_ai_riddle, name='generate_ai_riddle'),
    path('mini-games/check-riddle/', views.check_riddle_answer, name='check_riddle_answer'),
    
    # AI Mystery Detective Game
    path('mini-games/mystery-detective/', views.ai_mystery_game, name='mystery_detective'),
    path('mini-games/generate-mystery/', views.generate_mystery, name='generate_mystery'),
    path('mini-games/ask-mystery-question/', views.ask_mystery_question, name='ask_mystery_question'),
    path('mini-games/solve-mystery/', views.solve_mystery, name='solve_mystery'),
    
    # AI Story Adventure Game
    path('mini-games/story-adventure/', views.ai_story_adventure, name='story_adventure'),
    path('mini-games/start-story/', views.start_story, name='start_story'),
    path('mini-games/continue-story/', views.continue_story, name='continue_story'),
    path('mini-games/end-story/', views.end_story, name='end_story'),
]