from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
import google.generativeai as genai
import json
import hashlib
import logging
import os
from time import time

from .models import Quiz, QuizAttempt, QuizQuestion, Leaderboard, UsedQuestion, QUIZ_GENRES, MiniGameScore, MiniGameLeaderboard

logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


@login_required
def games_home(request):
    """Games landing page with Mini Games and Quiz sections"""
    context = {
        'quiz_genres': QUIZ_GENRES,
    }
    return render(request, 'games/games_home.html', context)


@login_required
def select_genre(request):
    """Genre selection page for quiz"""
    if request.method == 'POST':
        genre = request.POST.get('genre')
        if genre and any(g[0] == genre for g in QUIZ_GENRES):
            return redirect(f'/games/quiz/generate/?genre={genre}')
        else:
            messages.error(request, 'Please select a valid genre.')
    
    context = {
        'quiz_genres': QUIZ_GENRES,
    }
    return render(request, 'games/select_genre.html', context)


def get_used_question_hashes(user, genre):
    """Get list of used question hashes for a user and genre"""
    return list(UsedQuestion.objects.filter(
        user=user, 
        genre=genre
    ).values_list('question_hash', flat=True))


def hash_question(question_text):
    """Create hash of question text"""
    return hashlib.sha256(question_text.lower().strip().encode()).hexdigest()


@login_required
def generate_quiz(request):
    """Generate quiz questions using Gemini AI"""
    genre = request.GET.get('genre')
    if not genre or not any(g[0] == genre for g in QUIZ_GENRES):
        messages.error(request, 'Invalid genre selected.')
        return redirect('games:select_genre')
    
    try:
        # Get used question hashes to avoid duplicates
        used_hashes = get_used_question_hashes(request.user, genre)
        
        # Get genre display name
        genre_name = dict(QUIZ_GENRES).get(genre, genre)
        
        # Create prompt for Gemini
        prompt = f"""You are an expert quiz generator specializing in {genre_name}.

Generate exactly 20 multiple-choice questions about {genre_name}. 

CRITICAL REQUIREMENTS:
1. Return ONLY a valid JSON array with no additional text, markdown, or code blocks
2. Each question must be unique and educational
3. Mix difficulty levels (easy, medium, hard)
4. Ensure questions are clear and unambiguous
5. All 4 options should be plausible but only one correct

JSON FORMAT (return this exact structure):
[
  {{
    "question": "Clear, specific question text here?",
    "options": [
      "Option A text",
      "Option B text", 
      "Option C text",
      "Option D text"
    ],
    "correct_answer": "Exact text of correct option",
    "difficulty": "easy|medium|hard"
  }}
]

Generate 20 questions now in the exact JSON format above. Do not include any markdown formatting or code blocks."""

        # Use Gemini 2.5 Flash for fast, efficient generation
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        
        # Parse response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        questions_data = json.loads(response_text)
        
        # Validate we have 20 questions
        if len(questions_data) != 20:
            raise ValueError(f"Expected 20 questions, got {len(questions_data)}")
        
        # Filter out used questions
        new_questions = []
        for q in questions_data:
            q_hash = hash_question(q['question'])
            if q_hash not in used_hashes:
                new_questions.append(q)
        
        # If we filtered too many, regenerate
        if len(new_questions) < 15:
            messages.warning(request, 'Generating fresh questions to avoid duplicates...')
            # Recursively try again (max 2 attempts to avoid infinite loop)
            if not request.session.get('regenerate_attempts', 0):
                request.session['regenerate_attempts'] = 1
                return generate_quiz(request)
            else:
                del request.session['regenerate_attempts']
                # Use what we have
                questions_data = new_questions[:20] if len(new_questions) >= 20 else questions_data[:20]
        else:
            questions_data = new_questions[:20]
        
        # Create Quiz object
        quiz = Quiz.objects.create(
            user=request.user,
            genre=genre,
            questions_data=questions_data
        )
        
        # Create QuizQuestion objects for analytics
        for idx, q_data in enumerate(questions_data, 1):
            QuizQuestion.objects.create(
                quiz=quiz,
                question_text=q_data['question'],
                options=q_data['options'],
                correct_answer=q_data['correct_answer'],
                difficulty=q_data.get('difficulty', 'medium'),
                question_number=idx
            )
            
            # Mark question as used
            q_hash = hash_question(q_data['question'])
            UsedQuestion.objects.get_or_create(
                user=request.user,
                genre=genre,
                question_hash=q_hash
            )
        
        # Create QuizAttempt
        QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            genre=genre
        )
        
        messages.success(request, f'Quiz ready! {len(questions_data)} questions generated. Good luck!')
        return redirect('games:take_quiz', quiz_id=quiz.pk)
        
    except json.JSONDecodeError as e:
        response_text_safe = locals().get('response_text', 'N/A')
        logger.error(f"JSON parsing error: {str(e)}\nResponse: {response_text_safe}")
        messages.error(request, 'Error generating quiz. Please try again.')
        return redirect('games:select_genre')
    except Exception as e:
        logger.error(f"Quiz generation error: {str(e)}")
        messages.error(request, 'Error generating quiz. Please try again.')
        return redirect('games:select_genre')


@login_required
def take_quiz(request, quiz_id):
    """Quiz taking interface"""
    quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)
    attempt = QuizAttempt.objects.filter(quiz=quiz, user=request.user, is_completed=False).first()
    
    if not attempt:
        messages.error(request, 'Quiz attempt not found.')
        return redirect('games:home')
    
    context = {
        'quiz': quiz,
        'attempt': attempt,
        'questions': quiz.questions_data,
        'total_questions': len(quiz.questions_data),
        'genre_display': dict(QUIZ_GENRES).get(quiz.genre, quiz.genre),
    }
    return render(request, 'games/take_quiz.html', context)


@login_required
@require_POST
def submit_answer(request):
    """Handle answer submission via AJAX"""
    try:
        data = json.loads(request.body)
        attempt_id = data.get('attempt_id')
        question_index = data.get('question_index')
        user_answer = data.get('answer')  # Can be answer text or 'skip'
        
        attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
        quiz = attempt.quiz
        
        # Get correct answer
        question_data = quiz.questions_data[question_index]
        correct_answer = question_data['correct_answer']
        
        # Update user_answers
        if attempt.user_answers is None:
            attempt.user_answers = {}
        
        attempt.user_answers[str(question_index)] = user_answer
        
        # Update counts
        if user_answer == 'skip':
            attempt.skipped_answers += 1
            is_correct = False
        elif user_answer == correct_answer:
            attempt.correct_answers += 1
            is_correct = True
        else:
            attempt.wrong_answers += 1
            is_correct = False
        
        attempt.save()
        
        return JsonResponse({
            'success': True,
            'is_correct': is_correct,
            'correct_answer': correct_answer,
        })
        
    except Exception as e:
        logger.error(f"Error submitting answer: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def complete_quiz(request, attempt_id):
    """Complete quiz and calculate final score"""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    
    if attempt.is_completed:
        return redirect('games:quiz_results', attempt_id=attempt_id)
    
    # Complete the quiz
    attempt.complete_quiz()
    
    # Update leaderboard
    update_leaderboard(request.user, attempt.genre)
    
    messages.success(request, 'Quiz completed! Here are your results.')
    return redirect('games:quiz_results', attempt_id=attempt_id)


def update_leaderboard(user, genre):
    """Update leaderboard entries for user"""
    # Update genre-specific leaderboard
    leaderboard, created = Leaderboard.objects.get_or_create(
        user=user,
        genre=genre
    )
    leaderboard.update_stats()
    
    # Update overall leaderboard
    overall_leaderboard, created = Leaderboard.objects.get_or_create(
        user=user,
        genre=None
    )
    overall_leaderboard.update_stats()


@login_required
def quiz_results(request, attempt_id):
    """Display quiz results and performance"""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    
    if not attempt.is_completed:
        messages.warning(request, 'Please complete the quiz first.')
        return redirect('games:take_quiz', quiz_id=attempt.quiz.pk)
    
    # Get user's leaderboard stats
    user_stats = Leaderboard.objects.filter(user=request.user, genre=attempt.genre).first()
    
    context = {
        'attempt': attempt,
        'quiz': attempt.quiz,
        'genre_display': dict(QUIZ_GENRES).get(attempt.genre, attempt.genre),
        'user_stats': user_stats,
    }
    return render(request, 'games/quiz_results.html', context)


@login_required
def continue_quiz(request):
    """Handle continue quiz logic"""
    if request.method == 'POST':
        action = request.POST.get('action')
        current_genre = request.POST.get('current_genre')
        
        if action == 'continue_same':
            # Generate new quiz with same genre
            return redirect(f'/games/quiz/generate/?genre={current_genre}')
        elif action == 'select_new':
            # Go to genre selection
            return redirect('games:select_genre')
        else:
            return redirect('games:home')
    
    return redirect('games:home')


@login_required
def analytics_dashboard(request):
    """User analytics dashboard"""
    genre_filter = request.GET.get('genre', None)
    
    # Get all attempts
    if genre_filter:
        attempts = QuizAttempt.objects.filter(
            user=request.user, 
            genre=genre_filter,
            is_completed=True
        ).order_by('-completed_at')
    else:
        attempts = QuizAttempt.objects.filter(
            user=request.user,
            is_completed=True
        ).order_by('-completed_at')
    
    # Calculate overall stats
    total_attempts = attempts.count()
    if total_attempts > 0:
        total_score = sum(a.score for a in attempts)
        avg_score = total_score / total_attempts
        highest_score = max(a.score for a in attempts)
        avg_accuracy = sum(a.accuracy for a in attempts) / total_attempts
    else:
        total_score = avg_score = highest_score = avg_accuracy = 0
    
    # Genre-wise stats
    genre_stats = []
    for genre_code, genre_name in QUIZ_GENRES:
        genre_attempts = QuizAttempt.objects.filter(
            user=request.user,
            genre=genre_code,
            is_completed=True
        )
        count = genre_attempts.count()
        if count > 0:
            genre_stats.append({
                'genre_code': genre_code,
                'genre_name': genre_name,
                'attempts': count,
                'total_score': sum(a.score for a in genre_attempts),
                'avg_score': sum(a.score for a in genre_attempts) / count,
                'avg_accuracy': sum(a.accuracy for a in genre_attempts) / count,
            })
    
    context = {
        'attempts': attempts[:20],  # Last 20 attempts
        'total_attempts': total_attempts,
        'total_score': total_score,
        'avg_score': round(avg_score, 2),
        'highest_score': highest_score,
        'avg_accuracy': round(avg_accuracy, 2),
        'genre_stats': genre_stats,
        'quiz_genres': QUIZ_GENRES,
        'selected_genre': genre_filter,
    }
    return render(request, 'games/analytics.html', context)


@login_required
def leaderboard(request):
    """Global and genre-wise leaderboard"""
    genre_filter = request.GET.get('genre', None)
    
    if genre_filter:
        # Genre-specific leaderboard
        leaderboard_entries = Leaderboard.objects.filter(
            genre=genre_filter
        ).order_by('-total_score', '-average_score')[:100]
        
        # Get user's rank
        user_entry = Leaderboard.objects.filter(
            user=request.user,
            genre=genre_filter
        ).first()
        
        if user_entry:
            user_rank = Leaderboard.objects.filter(
                genre=genre_filter,
                total_score__gt=user_entry.total_score
            ).count() + 1
        else:
            user_rank = None
        
        # Format genre display name
        genre_display = dict(QUIZ_GENRES).get(genre_filter, genre_filter)
    else:
        # Overall leaderboard
        leaderboard_entries = Leaderboard.objects.filter(
            genre=None
        ).order_by('-total_score', '-average_score')[:100]
        
        # Get user's rank
        user_entry = Leaderboard.objects.filter(
            user=request.user,
            genre=None
        ).first()
        
        if user_entry:
            user_rank = Leaderboard.objects.filter(
                genre=None,
                total_score__gt=user_entry.total_score
            ).count() + 1
        else:
            user_rank = None
        
        genre_display = None
    
    # Top 10 for display
    top_10 = leaderboard_entries[:10]
    
    context = {
        'top_10': top_10,
        'user_entry': user_entry,
        'user_rank': user_rank,
        'quiz_genres': QUIZ_GENRES,
        'selected_genre': genre_filter,
        'genre_display': genre_display,
        'total_players': leaderboard_entries.count(),
    }
    return render(request, 'games/leaderboard.html', context)


# ============================================
# MINI GAMES VIEWS
# ============================================

@login_required
def mini_games_home(request):
    """Mini games selection page"""
    # Get user's best scores for each game
    user_scores = {}
    for game_type, game_name in MiniGameScore.GAME_TYPES:
        best_score = MiniGameScore.objects.filter(
            user=request.user,
            game_type=game_type,
            completed=True
        ).order_by('-score').first()
        user_scores[game_type] = best_score
    
    context = {
        'user_scores': user_scores,
    }
    return render(request, 'games/mini_games_home.html', context)


@login_required
def memory_match_game(request):
    """Memory match card game"""
    difficulty = request.GET.get('difficulty', 'medium')
    
    # Ensure difficulty is valid
    valid_difficulties = ['easy', 'medium', 'hard']
    if difficulty not in valid_difficulties:
        difficulty = 'medium'
    
    # Define grid sizes based on difficulty
    grid_sizes = {
        'easy': 4,    # 4x4 = 16 cards (8 pairs)
        'medium': 6,  # 6x6 = 36 cards (18 pairs)
        'hard': 8,    # 8x8 = 64 cards (32 pairs)
    }
    
    grid_size = grid_sizes.get(difficulty, 6)
    
    print(f"Memory Match - Difficulty: {difficulty}, Grid Size: {grid_size}")  # Debug log
    
    context = {
        'difficulty': difficulty,
        'grid_size': grid_size,
    }
    return render(request, 'games/memory_match.html', context)


@login_required
def pattern_recognition_game(request):
    """Pattern recognition game"""
    difficulty = request.GET.get('difficulty', 'medium')
    
    context = {
        'difficulty': difficulty,
    }
    return render(request, 'games/pattern_recognition.html', context)


@login_required
def logic_puzzle_game(request):
    """Logic puzzle game (Number puzzle - similar to 2048)"""
    difficulty = request.GET.get('difficulty', 'medium')
    
    context = {
        'difficulty': difficulty,
    }
    return render(request, 'games/logic_puzzle.html', context)


@login_required
@require_POST
def save_minigame_score(request):
    """Save mini game score via AJAX"""
    try:
        data = json.loads(request.body)
        game_type = data.get('game_type')
        difficulty = data.get('difficulty', 'medium')
        score = int(data.get('score', 0))
        time_taken = float(data.get('time_taken', 0))
        moves_count = int(data.get('moves_count', 0))
        completed = data.get('completed', True)
        
        # Create score entry
        minigame_score = MiniGameScore.objects.create(
            user=request.user,
            game_type=game_type,
            difficulty=difficulty,
            score=score,
            time_taken=time_taken,
            moves_count=moves_count,
            completed=completed
        )
        
        # Update leaderboard
        leaderboard, created = MiniGameLeaderboard.objects.get_or_create(
            user=request.user,
            game_type=game_type
        )
        leaderboard.update_stats()
        
        # Get user's rank
        rank = MiniGameLeaderboard.objects.filter(
            game_type=game_type,
            total_score__gt=leaderboard.total_score
        ).count() + 1
        
        return JsonResponse({
            'success': True,
            'score_id': minigame_score.id,
            'rank': rank,
            'high_score': leaderboard.highest_score,
            'message': 'Score saved successfully!'
        })
        
    except Exception as e:
        logger.error(f"Error saving mini game score: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def minigame_leaderboard(request):
    """Leaderboard for mini games with difficulty breakdown"""
    # Get leaderboards for all game types and difficulties
    memory_match_easy = MiniGameScore.objects.filter(
        game_type='memory_match',
        difficulty='easy',
        completed=True
    ).select_related('user').order_by('-score')[:10]
    
    memory_match_medium = MiniGameScore.objects.filter(
        game_type='memory_match',
        difficulty='medium',
        completed=True
    ).select_related('user').order_by('-score')[:10]
    
    memory_match_hard = MiniGameScore.objects.filter(
        game_type='memory_match',
        difficulty='hard',
        completed=True
    ).select_related('user').order_by('-score')[:10]
    
    pattern_recognition_easy = MiniGameScore.objects.filter(
        game_type='pattern_recognition',
        difficulty='easy',
        completed=True
    ).select_related('user').order_by('-score')[:10]
    
    pattern_recognition_medium = MiniGameScore.objects.filter(
        game_type='pattern_recognition',
        difficulty='medium',
        completed=True
    ).select_related('user').order_by('-score')[:10]
    
    pattern_recognition_hard = MiniGameScore.objects.filter(
        game_type='pattern_recognition',
        difficulty='hard',
        completed=True
    ).select_related('user').order_by('-score')[:10]
    
    logic_puzzle_easy = MiniGameScore.objects.filter(
        game_type='logic_puzzle',
        difficulty='easy',
        completed=True
    ).select_related('user').order_by('-score')[:10]
    
    logic_puzzle_medium = MiniGameScore.objects.filter(
        game_type='logic_puzzle',
        difficulty='medium',
        completed=True
    ).select_related('user').order_by('-score')[:10]
    
    logic_puzzle_hard = MiniGameScore.objects.filter(
        game_type='logic_puzzle',
        difficulty='hard',
        completed=True
    ).select_related('user').order_by('-score')[:10]
    
    mystery_detective_easy = MiniGameScore.objects.filter(
        game_type='mystery_detective',
        difficulty='easy',
        completed=True
    ).select_related('user').order_by('-score')[:10]
    
    mystery_detective_medium = MiniGameScore.objects.filter(
        game_type='mystery_detective',
        difficulty='medium',
        completed=True
    ).select_related('user').order_by('-score')[:10]
    
    mystery_detective_hard = MiniGameScore.objects.filter(
        game_type='mystery_detective',
        difficulty='hard',
        completed=True
    ).select_related('user').order_by('-score')[:10]
    
    story_adventure_easy = MiniGameScore.objects.filter(
        game_type='story_adventure',
        difficulty='easy',
        completed=True
    ).select_related('user').order_by('-score')[:10]
    
    story_adventure_medium = MiniGameScore.objects.filter(
        game_type='story_adventure',
        difficulty='medium',
        completed=True
    ).select_related('user').order_by('-score')[:10]
    
    story_adventure_hard = MiniGameScore.objects.filter(
        game_type='story_adventure',
        difficulty='hard',
        completed=True
    ).select_related('user').order_by('-score')[:10]
    
    context = {
        'memory_match_easy': memory_match_easy,
        'memory_match_medium': memory_match_medium,
        'memory_match_hard': memory_match_hard,
        'pattern_recognition_easy': pattern_recognition_easy,
        'pattern_recognition_medium': pattern_recognition_medium,
        'pattern_recognition_hard': pattern_recognition_hard,
        'logic_puzzle_easy': logic_puzzle_easy,
        'logic_puzzle_medium': logic_puzzle_medium,
        'logic_puzzle_hard': logic_puzzle_hard,
        'mystery_detective_easy': mystery_detective_easy,
        'mystery_detective_medium': mystery_detective_medium,
        'mystery_detective_hard': mystery_detective_hard,
        'story_adventure_easy': story_adventure_easy,
        'story_adventure_medium': story_adventure_medium,
        'story_adventure_hard': story_adventure_hard,
    }
    return render(request, 'games/minigame_leaderboard.html', context)


# ============================================
# AI-POWERED MINI GAME FEATURES
# ============================================

@login_required
@require_POST
def get_ai_hint(request):
    """Get AI-powered hint using Gemini for mini games"""
    try:
        data = json.loads(request.body)
        game_type = data.get('game_type')
        current_state = data.get('current_state', {})
        difficulty = data.get('difficulty', 'medium')
        
        # Construct context-aware prompt
        prompts = {
            'memory_match': f"""You are a helpful memory game coach. The player is playing a memory card matching game on {difficulty} difficulty.
            
Current situation:
- Moves made: {current_state.get('moves', 0)}
- Matches found: {current_state.get('matches', 0)}
- Time elapsed: {current_state.get('time', 0)} seconds

Provide a short, encouraging tip (max 2 sentences) about memory techniques or strategy. Be motivational and specific.""",
            
            'pattern_recognition': f"""You are a pattern recognition expert coach. The player is playing a Simon-says style pattern memory game on {difficulty} difficulty.
            
Current situation:
- Current level: {current_state.get('level', 1)}
- Lives remaining: {current_state.get('lives', 3)}
- Longest streak: {current_state.get('streak', 0)}

Provide a short, helpful tip (max 2 sentences) about pattern memorization technique or focus strategy.""",
            
            'logic_puzzle': f"""You are a puzzle strategy expert. The player is playing a 2048-style logic puzzle on {difficulty} difficulty.
            
Current situation:
- Current score: {current_state.get('score', 0)}
- Moves made: {current_state.get('moves', 0)}
- Highest tile: {current_state.get('best_tile', 2)}

Provide a short, strategic tip (max 2 sentences) about tile positioning or merging strategy. Be specific and actionable."""
        }
        
        prompt = prompts.get(game_type, "Provide an encouraging gaming tip in max 2 sentences.")
        
        # Generate hint using Gemini
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        hint_text = response.text.strip()
        
        return JsonResponse({
            'success': True,
            'hint': hint_text
        })
        
    except Exception as e:
        logger.error(f"Error generating AI hint: {e}")
        return JsonResponse({
            'success': False,
            'hint': "Focus on strategy and take your time! You've got this! 🎯"
        })


@login_required
def ai_riddle_game(request):
    """AI-powered riddle/brain teaser game"""
    difficulty = request.GET.get('difficulty', 'medium')
    
    context = {
        'difficulty': difficulty,
    }
    return render(request, 'games/ai_riddle_game.html', context)


@login_required
@require_POST
def generate_ai_riddle(request):
    """Generate a new riddle using Gemini AI"""
    try:
        data = json.loads(request.body)
        difficulty = data.get('difficulty', 'medium')
        category = data.get('category', 'general')
        
        difficulty_prompts = {
            'easy': "Create a simple, fun riddle suitable for beginners. Keep it light and entertaining.",
            'medium': "Create a moderately challenging riddle that requires logical thinking.",
            'hard': "Create a very challenging riddle that requires deep lateral thinking and creative problem-solving."
        }
        
        prompt = f"""{difficulty_prompts.get(difficulty, difficulty_prompts['medium'])}

Category: {category}

Generate ONE riddle in the following JSON format ONLY (no additional text):
{{
    "riddle": "The riddle question",
    "answer": "The correct answer (short, 1-3 words)",
    "explanation": "Brief explanation of the answer",
    "hints": ["hint 1", "hint 2", "hint 3"],
    "difficulty_points": 100 or 200 or 300 depending on difficulty
}}

Make it engaging and creative!"""
        
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Extract JSON from response
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        riddle_data = json.loads(result_text)
        
        return JsonResponse({
            'success': True, 
            'riddle': riddle_data
        })
        
    except Exception as e:
        logger.error(f"Error generating riddle: {e}")
        # Fallback riddle
        return JsonResponse({
            'success': True,
            'riddle': {
                'riddle': "I speak without a mouth and hear without ears. I have no body, but come alive with wind. What am I?",
                'answer': "echo",
                'explanation': "An echo is a sound that bounces back, seeming to 'speak' without having a mouth.",
                'hints': ["Think about sound", "It repeats what you say", "Found in empty spaces"],
                'difficulty_points': 100
            }
        })


@login_required
@require_POST
def check_riddle_answer(request):
    """Check user's answer for the riddle"""
    try:
        data = json.loads(request.body)
        user_answer = data.get('answer', '').strip().lower()
        correct_answer = data.get('correct_answer', '').strip().lower()
        riddle_text = data.get('riddle', '')
        
        # Use AI to check if answer is correct (handles synonyms and variations)
        prompt = f"""You are a riddle answer validator.

Riddle: {riddle_text}
Correct Answer: {correct_answer}
User's Answer: {user_answer}

Is the user's answer correct? Consider synonyms, variations, and alternative phrasings.
Respond with ONLY a JSON object:
{{
    "is_correct": true or false,
    "feedback": "Brief friendly feedback message"
}}"""
        
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Extract JSON
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(result_text)
        
        return JsonResponse({
            'success': True,
            'is_correct': result.get('is_correct', False),
            'feedback': result.get('feedback', 'Good try!')
        })
        
    except Exception as e:
        logger.error(f"Error checking riddle answer: {e}")
        # Simple fallback comparison
        is_correct = user_answer == correct_answer
        return JsonResponse({
            'success': True,
            'is_correct': is_correct,
            'feedback': "Correct! 🎉" if is_correct else "Not quite, try again! 💭"
        })


# ============== AI MYSTERY DETECTIVE GAME ==============

@login_required
def ai_mystery_game(request):
    """AI-powered mystery detective game"""
    difficulty = request.GET.get('difficulty', 'medium')
    
    if difficulty not in ['easy', 'medium', 'hard']:
        difficulty = 'medium'
    
    context = {
        'difficulty': difficulty
    }
    return render(request, 'games/ai_mystery_game.html', context)


@login_required
@require_POST
def generate_mystery(request):
    """Generate a unique mystery scenario using Gemini AI"""
    try:
        data = json.loads(request.body)
        difficulty = data.get('difficulty', 'medium')
        
        # Define complexity by difficulty
        complexity_map = {
            'easy': {
                'suspects': 3,
                'clues': 4,
                'complexity': 'simple with obvious clues',
                'max_questions': 8,
                'points': 100
            },
            'medium': {
                'suspects': 4,
                'clues': 6,
                'complexity': 'moderate with some red herrings',
                'max_questions': 6,
                'points': 200
            },
            'hard': {
                'suspects': 5,
                'clues': 8,
                'complexity': 'complex with multiple red herrings and subtle connections',
                'max_questions': 5,
                'points': 300
            }
        }
        
        config = complexity_map.get(difficulty, complexity_map['medium'])
        
        prompt = f"""Generate a unique detective mystery scenario for a {difficulty} difficulty game.

Requirements:
- Create a compelling mystery story ({config['complexity']})
- Include exactly {config['suspects']} suspects with names, motives, and alibis
- Include {config['clues']} clues (some should be red herrings for harder difficulties)
- One suspect must be the true culprit with a logical explanation
- The scenario should be solvable through questioning and deduction

Return ONLY a JSON object with this structure:
{{
    "title": "Brief catchy title",
    "scenario": "200-word engaging mystery description with the crime and initial scene",
    "location": "Where the mystery takes place",
    "victim": "Name and brief description",
    "suspects": [
        {{
            "name": "Full name",
            "role": "Their relationship to victim/location",
            "motive": "Why they might have done it",
            "alibi": "Their claimed whereabouts",
            "secret": "Hidden information that can be discovered through questioning"
        }}
    ],
    "clues": [
        {{
            "description": "What was found/observed",
            "significance": "What it actually means (hidden from player initially)",
            "is_red_herring": false
        }}
    ],
    "culprit": "Name of the actual guilty party",
    "solution": "Detailed explanation of how the crime was committed and why",
    "max_questions": {config['max_questions']},
    "points": {config['points']}
}}

Make it creative and engaging!"""

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Extract JSON
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        mystery = json.loads(result_text)
        
        # Store mystery in session for later validation
        request.session['current_mystery'] = mystery
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'mystery': {
                'title': mystery['title'],
                'scenario': mystery['scenario'],
                'location': mystery['location'],
                'victim': mystery['victim'],
                'suspects': mystery['suspects'],
                'visible_clues': [{'description': c['description']} for c in mystery['clues']],
                'max_questions': mystery['max_questions'],
                'points': mystery['points']
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating mystery: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to generate mystery. Please try again.'
        }, status=500)


@login_required
@require_POST
def ask_mystery_question(request):
    """Handle player questions about the mystery with intelligent AI responses"""
    try:
        data = json.loads(request.body)
        question = data.get('question', '').strip()
        questions_asked = data.get('questions_asked', 0)
        
        if not question:
            return JsonResponse({
                'success': False,
                'error': 'Please ask a question.'
            })
        
        # Get mystery from session
        mystery = request.session.get('current_mystery')
        if not mystery:
            return JsonResponse({
                'success': False,
                'error': 'No active mystery found. Please start a new game.'
            })
        
        # Check if questions remaining
        if questions_asked >= mystery['max_questions']:
            return JsonResponse({
                'success': False,
                'error': 'No questions remaining! Make your accusation.'
            })
        
        prompt = f"""You are an AI detective game narrator. A player is investigating this mystery:

MYSTERY DETAILS (SECRET - Don't reveal everything at once):
Scenario: {mystery['scenario']}
Location: {mystery['location']}
Victim: {mystery['victim']}
Culprit: {mystery['culprit']}
Solution: {mystery['solution']}

Suspects: {json.dumps(mystery['suspects'], indent=2)}
Clues: {json.dumps(mystery['clues'], indent=2)}

The player asks: "{question}"

Provide a helpful response that:
1. Answers their specific question with relevant information
2. Reveals clues naturally without making it too obvious
3. Stays in character as a detective game narrator
4. Gives them information to work with but doesn't directly reveal the culprit
5. If they ask about a specific suspect, reveal their secret if relevant
6. Keep response under 100 words, clear and engaging

Return only the narrative response text (no JSON, no quotes)."""

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        answer = response.text.strip()
        
        # Remove quotes if present
        answer = answer.strip('"\'')
        
        return JsonResponse({
            'success': True,
            'answer': answer,
            'questions_remaining': mystery['max_questions'] - questions_asked - 1
        })
        
    except Exception as e:
        logger.error(f"Error answering mystery question: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to process question. Please try again.'
        }, status=500)


@login_required
@require_POST
def solve_mystery(request):
    """Evaluate player's solution using AI"""
    try:
        data = json.loads(request.body)
        accused = data.get('accused', '').strip()
        reasoning = data.get('reasoning', '').strip()
        questions_used = data.get('questions_used', 0)
        time_taken = data.get('time_taken', 0)
        
        if not accused:
            return JsonResponse({
                'success': False,
                'error': 'Please select a suspect to accuse.'
            })
        
        # Get mystery from session
        mystery = request.session.get('current_mystery')
        if not mystery:
            return JsonResponse({
                'success': False,
                'error': 'No active mystery found.'
            })
        
        culprit = mystery['culprit']
        is_correct = accused.lower() == culprit.lower()
        
        # Calculate score
        base_points = mystery['points']
        if is_correct:
            # Bonus for fewer questions used
            efficiency_bonus = int((mystery['max_questions'] - questions_used) * 20)
            # Time bonus (up to 50 points for solving quickly)
            time_bonus = max(0, 50 - int(time_taken / 10))
            total_score = base_points + efficiency_bonus + time_bonus
        else:
            total_score = 0
        
        # Use AI to evaluate reasoning
        prompt = f"""Evaluate this detective game solution:

The correct culprit was: {culprit}
Player accused: {accused}
Player's reasoning: {reasoning if reasoning else "No reasoning provided"}

True solution: {mystery['solution']}

Provide feedback that:
1. Confirms if they're correct or wrong
2. If wrong, explain what they missed without being condescending
3. If correct, praise their deductive reasoning
4. Reveal the full solution
5. Keep it under 150 words, engaging and fun

Return only the feedback text (no JSON)."""

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        feedback = response.text.strip().strip('"\'')
        
        # Save score to database if correct
        if is_correct:
            try:
                game_score = MiniGameScore.objects.create(
                    user=request.user,
                    game_type='mystery_detective',
                    difficulty=mystery.get('difficulty', 'medium'),
                    score=total_score,
                    time_taken=time_taken,
                    moves_count=questions_used,
                    completed=True
                )
                
                # Update leaderboard
                leaderboard, created = MiniGameLeaderboard.objects.get_or_create(
                    user=request.user,
                    game_type='mystery_detective'
                )
                
                if total_score > leaderboard.best_score:
                    leaderboard.best_score = total_score
                    leaderboard.games_played += 1
                    leaderboard.save()
                elif created:
                    leaderboard.best_score = total_score
                    leaderboard.games_played = 1
                    leaderboard.save()
                else:
                    leaderboard.games_played += 1
                    leaderboard.save()
                    
            except Exception as e:
                logger.error(f"Error saving mystery game score: {e}")
        
        # Clear mystery from session
        if 'current_mystery' in request.session:
            del request.session['current_mystery']
            request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'is_correct': is_correct,
            'feedback': feedback,
            'score': total_score,
            'correct_culprit': culprit,
            'full_solution': mystery['solution']
        })
        
    except Exception as e:
        logger.error(f"Error solving mystery: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to evaluate solution. Please try again.'
        }, status=500)


# ============== AI STORY ADVENTURE GAME ==============

@login_required
def ai_story_adventure(request):
    """AI-powered interactive story adventure game"""
    genre = request.GET.get('genre', 'fantasy')
    
    valid_genres = ['fantasy', 'scifi', 'mystery', 'horror', 'adventure']
    if genre not in valid_genres:
        genre = 'fantasy'
    
    context = {
        'genre': genre
    }
    return render(request, 'games/ai_story_adventure.html', context)


@login_required
@require_POST
def start_story(request):
    """Generate initial story scenario using Gemini AI"""
    try:
        data = json.loads(request.body)
        genre = data.get('genre', 'fantasy')
        
        genre_settings = {
            'fantasy': {
                'name': 'Fantasy Adventure',
                'description': 'magical realms, dragons, and epic quests',
                'setting': 'a mystical fantasy world with magic and mythical creatures',
                'themes': 'heroism, magic, destiny, good vs evil'
            },
            'scifi': {
                'name': 'Sci-Fi Odyssey',
                'description': 'space exploration, AI, and futuristic technology',
                'setting': 'a futuristic sci-fi universe with advanced technology and alien civilizations',
                'themes': 'technology, exploration, humanity, survival'
            },
            'mystery': {
                'name': 'Mystery Thriller',
                'description': 'suspense, secrets, and unexpected twists',
                'setting': 'a mysterious location with secrets to uncover',
                'themes': 'investigation, deception, revelation, suspense'
            },
            'horror': {
                'name': 'Horror Tale',
                'description': 'supernatural terror and psychological thrills',
                'setting': 'a dark and eerie environment filled with dread',
                'themes': 'fear, survival, the unknown, psychological horror'
            },
            'adventure': {
                'name': 'Action Adventure',
                'description': 'treasure hunts, exploration, and danger',
                'setting': 'an exotic location ripe for exploration and discovery',
                'themes': 'exploration, danger, treasure, courage'
            }
        }
        
        settings = genre_settings.get(genre, genre_settings['fantasy'])
        
        prompt = f"""Create an engaging interactive story opening for a {settings['name']} game.

Setting: {settings['setting']}
Themes: {settings['themes']}

Requirements:
- Start with an intriguing hook that draws the player in
- Establish the setting and atmosphere vividly (150-200 words)
- Introduce the main character (the player) and their situation
- Present a clear inciting incident or challenge
- Provide exactly 3 compelling choices for what to do next
- Each choice should lead to different story branches

Return ONLY a JSON object:
{{
    "opening": "The story opening (150-200 words)",
    "situation": "Brief summary of current situation",
    "choices": [
        {{
            "id": 1,
            "text": "Choice description",
            "type": "action/dialogue/investigation"
        }},
        {{
            "id": 2,
            "text": "Choice description",
            "type": "action/dialogue/investigation"
        }},
        {{
            "id": 3,
            "text": "Choice description",
            "type": "action/dialogue/investigation"
        }}
    ]
}}

Make it immersive and exciting!"""

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Extract JSON
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        story_data = json.loads(result_text)
        
        # Initialize story session
        request.session['story_data'] = {
            'genre': genre,
            'chapter': 1,
            'choices_made': [],
            'story_path': [story_data['opening']],
            'start_time': time()
        }
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'story': story_data
        })
        
    except Exception as e:
        logger.error(f"Error starting story: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to generate story. Please try again.'
        }, status=500)


@login_required
@require_POST
def continue_story(request):
    """Continue story based on player's choice using AI"""
    try:
        data = json.loads(request.body)
        choice_id = data.get('choice_id')
        choice_text = data.get('choice_text', '')
        
        # Get story from session
        story_data = request.session.get('story_data')
        if not story_data:
            return JsonResponse({
                'success': False,
                'error': 'No active story found. Please start a new game.'
            })
        
        # Record choice
        story_data['choices_made'].append({
            'chapter': story_data['chapter'],
            'choice_id': choice_id,
            'choice_text': choice_text
        })
        
        # Check if this should be ending
        is_ending = story_data['chapter'] >= 5  # Story ends after 5 chapters
        
        # Generate next part
        prompt = f"""Continue this interactive {story_data['genre']} story based on the player's choice.

Previous story path:
{' '.join(story_data['story_path'][-2:] if len(story_data['story_path']) > 1 else story_data['story_path'])}

Player chose: "{choice_text}"

Chapter: {story_data['chapter'] + 1}

Requirements:
- Write 100-150 words continuing the story based on the choice
- Show immediate consequences of their decision
- Build tension and excitement
- {"Provide 3 new choices that advance the story" if not is_ending else "Provide a satisfying conclusion with an ending type"}

Return ONLY a JSON object:
{{
    "narrative": "The story continuation (100-150 words)",
    "situation": "Brief summary of new situation",
    {"choices" if not is_ending else "ending"}: {
        "[3 choice objects]" if not is_ending else 
        '{"type": "victory/tragedy/twist/bittersweet", "title": "Ending title", "description": "What happened"}'
    }
}}"""

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Extract JSON
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        continuation = json.loads(result_text)
        
        # Update story session
        story_data['chapter'] += 1
        story_data['story_path'].append(continuation['narrative'])
        request.session['story_data'] = story_data
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'continuation': continuation,
            'chapter': story_data['chapter'],
            'is_ending': is_ending
        })
        
    except Exception as e:
        logger.error(f"Error continuing story: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to continue story. Please try again.'
        }, status=500)


@login_required
@require_POST  
def end_story(request):
    """Save story completion and calculate score"""
    try:
        data = json.loads(request.body)
        ending_type = data.get('ending_type', 'neutral')
        
        # Get story from session
        story_data = request.session.get('story_data')
        if not story_data:
            return JsonResponse({
                'success': False,
                'error': 'No active story found.'
            })
        
        # Calculate score
        time_taken = int(time() - story_data.get('start_time', time()))
        chapters_completed = story_data['chapter']
        choices_made = len(story_data['choices_made'])
        
        # Base score by ending type
        ending_scores = {
            'victory': 300,
            'twist': 250,
            'bittersweet': 200,
            'tragedy': 150,
            'neutral': 100
        }
        
        base_score = ending_scores.get(ending_type, 100)
        chapter_bonus = chapters_completed * 50
        engagement_bonus = min(choices_made * 20, 100)
        
        total_score = base_score + chapter_bonus + engagement_bonus
        
        # Determine difficulty based on genre
        difficulty_map = {
            'fantasy': 'easy',
            'adventure': 'easy',
            'mystery': 'medium',
            'scifi': 'medium',
            'horror': 'hard'
        }
        difficulty = difficulty_map.get(story_data['genre'], 'medium')
        
        # Save to database
        try:
            game_score = MiniGameScore.objects.create(
                user=request.user,
                game_type='story_adventure',
                difficulty=difficulty,
                score=total_score,
                time_taken=time_taken,
                moves_count=choices_made,
                completed=True
            )
            
            # Update leaderboard
            leaderboard, created = MiniGameLeaderboard.objects.get_or_create(
                user=request.user,
                game_type='story_adventure'
            )
            
            if total_score > leaderboard.best_score:
                leaderboard.best_score = total_score
                leaderboard.games_played += 1
                leaderboard.save()
            elif created:
                leaderboard.best_score = total_score
                leaderboard.games_played = 1
                leaderboard.save()
            else:
                leaderboard.games_played += 1
                leaderboard.save()
                
        except Exception as e:
            logger.error(f"Error saving story adventure score: {e}")
        
        # Clear story from session
        if 'story_data' in request.session:
            del request.session['story_data']
            request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'score': total_score,
            'stats': {
                'chapters': chapters_completed,
                'choices': choices_made,
                'time': time_taken,
                'ending': ending_type
            }
        })
        
    except Exception as e:
        logger.error(f"Error ending story: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to save story. Please try again.'
        }, status=500)
