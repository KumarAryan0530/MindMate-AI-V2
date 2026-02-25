"""
Quick test script to verify Gemini API integration for quiz generation
Run this to ensure the API key is working before testing the full system
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'perplex.settings')
django.setup()

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def test_gemini_api():
    """Test Gemini API connection and quiz generation"""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY not found in environment variables")
        print("Please set GEMINI_API_KEY in your .env file")
        return False
    
    print("✓ API Key found")
    print(f"Key preview: {api_key[:10]}...{api_key[-10:]}")
    
    try:
        genai.configure(api_key=api_key)
        print("✓ Gemini API configured successfully")
        
        # Test with a simple prompt
        print("\n🧪 Testing quiz generation (5 sample questions)...")
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        prompt = """Generate exactly 5 multiple-choice questions about Mental Health.

Return ONLY a valid JSON array with no additional text, markdown, or code blocks.

JSON FORMAT:
[
  {
    "question": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "Exact text of correct option",
    "difficulty": "easy|medium|hard"
  }
]

Generate 5 questions now."""

        response = model.generate_content(prompt)
        print("\n✓ Response received from Gemini")
        print(f"Response preview:\n{response.text[:500]}...\n")
        
        # Try to parse as JSON
        import json
        response_text = response.text.strip()
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        questions = json.loads(response_text)
        print(f"✓ Successfully parsed {len(questions)} questions")
        
        # Display first question
        if questions:
            q = questions[0]
            print("\n📝 Sample Question:")
            print(f"Q: {q['question']}")
            print(f"Difficulty: {q['difficulty']}")
            print("Options:")
            for i, opt in enumerate(q['options'], 1):
                print(f"  {i}. {opt}")
            print(f"Correct: {q['correct_answer']}")
        
        print("\n✅ All tests passed! Gemini API is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nPlease check:")
        print("1. GEMINI_API_KEY is valid")
        print("2. You have internet connection")
        print("3. Gemini API quota is not exceeded")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Testing Gemini API Integration for Quiz Generation")
    print("=" * 60)
    print()
    
    success = test_gemini_api()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Ready to use the quiz feature!")
        print("\nNext steps:")
        print("1. Start the Django server: python manage.py runserver")
        print("2. Navigate to http://localhost:8000/games/")
        print("3. Select a genre and start your quiz!")
    else:
        print("❌ Please fix the errors above before using the quiz feature")
    print("=" * 60)
