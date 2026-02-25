"""
API Configuration Test Script for SafeMind-AI

This script tests whether your API keys are properly configured and working.
Run this before starting the Django application to verify API connectivity.

Usage:
    E:\all-projects\MindMate-AI\venv\Scripts\python.exe test_apis.py
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def test_gemini():
    """Test Google Gemini API"""
    print("📱 Testing Google Gemini API...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        print("   Please add your API key to the .env file")
        print("   Get your key from: https://aistudio.google.com/apikey")
        return False
    
    print(f"   API Key found: {api_key[:20]}...{api_key[-4:]}")
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        
        # Test with gemini-2.5-flash (used in chatbot)
        print("   Testing gemini-2.5-flash model...")
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content("Say 'Hello, SafeMind-AI is working!'")
        
        print("✅ Gemini API is working perfectly!")
        print(f"   Response: {response.text[:80]}...")
        return True
        
    except ImportError:
        print("❌ google-generativeai package not installed")
        print("   Run: pip install google-generativeai")
        return False
    except Exception as e:
        print(f"❌ Gemini API error: {str(e)}")
        print("   Check if your API key is valid and active")
        return False

def test_cloudflare():
    """Test Cloudflare AI API"""
    print("☁️  Testing Cloudflare AI API...")
    
    token = os.getenv("CLOUDFLARE_API_TOKEN")
    account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    
    if not token:
        print("❌ CLOUDFLARE_API_TOKEN not found in .env file")
        print("   Please add your token to the .env file")
        print("   Get your token from: https://dash.cloudflare.com/profile/api-tokens")
        return False
    
    if not account_id:
        print("❌ CLOUDFLARE_ACCOUNT_ID not found in .env file")
        print("   Please add your account ID to the .env file")
        print("   Find it at: https://dash.cloudflare.com/")
        return False
    
    print(f"   Token found: {token[:20]}...{token[-4:]}")
    print(f"   Account ID: {account_id}")
    
    try:
        import requests
        
        url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/huggingface/distilbert-sst-2-int8"
        headers = {"Authorization": f"Bearer {token}"}
        
        print("   Testing sentiment analysis model...")
        response = requests.post(
            url, 
            headers=headers, 
            json={"text": "I am very happy and excited!"}, 
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Cloudflare API is working perfectly!")
            print(f"   Response: {result.get('result', [])}")
            return True
        else:
            print(f"❌ Cloudflare API error: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            print("   Check if your token has 'Workers AI' permissions")
            return False
            
    except ImportError:
        print("❌ requests package not installed")
        print("   Run: pip install requests")
        return False
    except Exception as e:
        print(f"❌ Cloudflare API error: {str(e)}")
        return False

def test_env_file():
    """Check if .env file exists"""
    print("📄 Checking environment configuration...")
    
    if not os.path.exists(".env"):
        print("❌ .env file not found!")
        print("   Please create a .env file based on .env.example")
        print("   Copy .env.example to .env and add your API keys")
        return False
    
    print("✅ .env file found")
    
    # Check for required variables
    required_vars = [
        "GEMINI_API_KEY",
        "CLOUDFLARE_API_TOKEN", 
        "CLOUDFLARE_ACCOUNT_ID"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Warning: Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n   Please add these to your .env file")
        return False
    
    print("✅ All required environment variables are set")
    return True

def main():
    """Main test function"""
    print_header("MindMate-AI API Configuration Test")
    
    print("This script will test your API configuration.")
    print("Make sure you have:")
    print("  1. Created a .env file (copy from .env.example)")
    print("  2. Added your API keys to the .env file")
    print("  3. Installed all required packages (pip install -r requirements.txt)")
    
    # Test environment file
    env_ok = test_env_file()
    if not env_ok:
        print("\n" + "="*60)
        print("⚠️  Please fix the environment configuration first!")
        print("="*60)
        return False
    
    print()
    
    # Test APIs
    gemini_ok = test_gemini()
    print()
    cloudflare_ok = test_cloudflare()
    
    # Summary
    print_header("Test Summary")
    
    results = {
        "Environment File": "✅ PASS" if env_ok else "❌ FAIL",
        "Google Gemini API": "✅ PASS" if gemini_ok else "❌ FAIL",
        "Cloudflare AI API": "✅ PASS" if cloudflare_ok else "❌ FAIL"
    }
    
    for test, status in results.items():
        print(f"  {test:.<40} {status}")
    
    all_passed = env_ok and gemini_ok and cloudflare_ok
    
    if all_passed:
        print("\n🎉 All tests passed! Your API configuration is ready.")
        print("   You can now start the Django application:")
        print("   E:\\all-projects\\SafeMind-AI\\venv\\Scripts\\python.exe manage.py runserver")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("   Refer to API_CONFIGURATION.md for detailed instructions.")
    
    print("\n" + "="*60 + "\n")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
