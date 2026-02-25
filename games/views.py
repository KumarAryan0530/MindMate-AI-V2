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

from .models import Quiz, QuizAttempt, QuizQuestion, Leaderboard, UsedQuestion, QUIZ_GENRES

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
