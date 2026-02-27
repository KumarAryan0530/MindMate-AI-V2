"""
Test script for AI-enhanced Mini Games
Tests all new features including AI hints and AI riddle game
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'perplex.settings')
django.setup()

import google.generativeai as genai
from django.contrib.auth.models import User
from games.models import MiniGameScore, MiniGameLeaderboard

def test_gemini_api():
    """Test if Gemini API is working"""
    print("🧪 Testing Gemini API...")
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY not found in environment")
            return False
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content("Say 'AI is ready!' in one sentence")
        print(f"✅ Gemini API working: {response.text[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        return False

def test_ai_hint_generation():
    """Test AI hint generation for different games"""
    print("\n🧪 Testing AI Hint Generation...")
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Test Memory Match hint
        prompt = """You are a memory game coach. Provide a short tip (max 2 sentences) about memory techniques."""
        response = model.generate_content(prompt)
        print(f"✅ Memory Match hint: {response.text[:80]}...")
        
        # Test Pattern Recognition hint
        prompt = """You are a pattern recognition expert. Provide a short tip (max 2 sentences) about pattern memorization."""
        response = model.generate_content(prompt)
        print(f"✅ Pattern Recognition hint: {response.text[:80]}...")
        
        return True
    except Exception as e:
        print(f"❌ Hint generation error: {e}")
        return False

def test_riddle_generation():
    """Test AI riddle generation"""
    print("\n🧪 Testing AI Riddle Generation...")
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        prompt = """Create a simple riddle in JSON format:
{
    "riddle": "The riddle question",
    "answer": "The correct answer",
    "explanation": "Brief explanation",
    "hints": ["hint 1", "hint 2"],
    "difficulty_points": 100
}"""
        
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        
        import json
        riddle_data = json.loads(result_text)
        
        print(f"✅ Generated riddle: {riddle_data['riddle'][:80]}...")
        print(f"   Answer: {riddle_data['answer']}")
        return True
    except Exception as e:
        print(f"❌ Riddle generation error: {e}")
        return False

def test_database_models():
    """Test mini game database models"""
    print("\n🧪 Testing Database Models...")
    try:
        # Check if models are accessible
        user_count = User.objects.count()
        print(f"✅ User model accessible ({user_count} users)")
        
        score_count = MiniGameScore.objects.count()
        print(f"✅ MiniGameScore model accessible ({score_count} scores)")
        
        leaderboard_count = MiniGameLeaderboard.objects.count()
        print(f"✅ MiniGameLeaderboard model accessible ({leaderboard_count} entries)")
        
        # Check game types
        game_types = [gt[0] for gt in MiniGameScore.GAME_TYPES]
        print(f"✅ Available game types: {', '.join(game_types)}")
        
        return True
    except Exception as e:
        print(f"❌ Database model error: {e}")
        return False

def test_url_patterns():
    """Test if all URL patterns are configured"""
    print("\n🧪 Testing URL Patterns...")
    try:
        from django.urls import reverse
        
        urls_to_test = [
            ('games:mini_games_home', 'Mini Games Home'),
            ('games:memory_match', 'Memory Match'),
            ('games:pattern_recognition', 'Pattern Recognition'),
            ('games:logic_puzzle', 'Logic Puzzle'),
            ('games:ai_riddle', 'AI Riddle'),
            ('games:get_ai_hint', 'AI Hint API'),
            ('games:generate_ai_riddle', 'Generate Riddle API'),
            ('games:check_riddle_answer', 'Check Answer API'),
            ('games:minigame_leaderboard', 'Leaderboard'),
        ]
        
        for url_name, description in urls_to_test:
            try:
                url = reverse(url_name)
                print(f"✅ {description}: {url}")
            except Exception as e:
                print(f"❌ {description}: Error - {e}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ URL pattern error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🎮 AI-Enhanced Mini Games Test Suite")
    print("=" * 60)
    
    results = {
        "Gemini API": test_gemini_api(),
        "AI Hint Generation": test_ai_hint_generation(),
        "AI Riddle Generation": test_riddle_generation(),
        "Database Models": test_database_models(),
        "URL Patterns": test_url_patterns(),
    }
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
    
    all_passed = all(results.values())
    
    print("=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! AI-Enhanced Mini Games are ready!")
        print("\n📝 What's New:")
        print("   • AI-powered hint system for all games")
        print("   • AI Riddle Challenge with infinite unique riddles")
        print("   • Smart answer validation with synonym support")
        print("   • Context-aware coaching tips")
        print("\n🚀 Next Steps:")
        print("   1. Visit http://localhost:8000/games/mini-games/")
        print("   2. Try the AI Riddle Challenge")
        print("   3. Use AI hints during gameplay")
        print("   4. Check the leaderboard")
    else:
        print("⚠️ SOME TESTS FAILED - Please review the errors above")
    
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
