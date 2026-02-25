"""
Test script to verify Twilio and ElevenLabs API connections
"""
import os
import sys
from dotenv import load_dotenv

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_twilio():
    """Test Twilio connection"""
    print("\n🔵 Testing Twilio...")
    try:
        from twilio.rest import Client
        
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        
        if not account_sid or not auth_token:
            print("❌ Twilio credentials not found in .env file")
            return False
        
        client = Client(account_sid, auth_token)
        account = client.api.accounts(account_sid).fetch()
        print(f"✅ Twilio connected! Account: {account.friendly_name}")
        print(f"   Account SID: {account_sid}")
        print(f"   Phone Number: {os.getenv('TWILIO_PHONE_NUMBER', 'Not set')}")
        return True
    except Exception as e:
        print(f"❌ Twilio error: {e}")
        return False


def test_elevenlabs():
    """Test ElevenLabs connection"""
    print("\n🔵 Testing ElevenLabs...")
    try:
        import requests
        
        api_key = os.getenv('ELEVENLABS_API_KEY')
        agent_id = os.getenv('ELEVENLABS_AGENT_ID')
        
        if not api_key or not agent_id:
            print("❌ ElevenLabs credentials not found in .env file")
            return False
        
        url = "https://api.elevenlabs.io/v1/convai/conversation/get_signed_url"
        params = {'agent_id': agent_id}
        headers = {'xi-api-key': api_key}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if 'signed_url' in data:
            print("✅ ElevenLabs connected! Signed URL obtained.")
            print(f"   Agent ID: {agent_id}")
            return True
        else:
            print("❌ No signed URL in response")
            return False
            
    except Exception as e:
        print(f"❌ ElevenLabs error: {e}")
        return False


def test_redis():
    """Test Redis connection"""
    print("\n🔵 Testing Redis...")
    try:
        import redis
        
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        r = redis.from_url(redis_url)
        r.ping()
        print("✅ Redis connected!")
        print(f"   URL: {redis_url}")
        return True
    except Exception as e:
        print(f"❌ Redis error: {e}")
        print("   Make sure Redis server is running: redis-server")
        return False


def main():
    """Main test function"""
    print("=" * 60)
    print("SafeMind-AI Voice API Connection Test")
    print("=" * 60)
    
    # Test all services
    twilio_ok = test_twilio()
    elevenlabs_ok = test_elevenlabs()
    redis_ok = test_redis()
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Twilio:      {'✅ Connected' if twilio_ok else '❌ Failed'}")
    print(f"ElevenLabs:  {'✅ Connected' if elevenlabs_ok else '❌ Failed'}")
    print(f"Redis:       {'✅ Connected' if redis_ok else '❌ Failed'}")
    print("=" * 60)
    
    if twilio_ok and elevenlabs_ok and redis_ok:
        print("\n✅ All services connected successfully!")
        print("\n📝 Next steps:")
        print("   1. Run database migrations")
        print("   2. Start Redis: redis-server")
        print("   3. Start Django: daphne perplex.asgi:application")
        print("   4. Start Celery worker: celery -A perplex worker -l info --pool=solo")
        print("   5. Start Celery beat: celery -A perplex beat -l info")
        print("   6. Start Ngrok: ngrok http 8000")
        return 0
    else:
        print("\n❌ Some services failed. Please check your configuration.")
        print("\n📝 Troubleshooting:")
        if not twilio_ok:
            print("   - Verify TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env")
            print("   - Get credentials from: https://console.twilio.com/")
        if not elevenlabs_ok:
            print("   - Verify ELEVENLABS_API_KEY and ELEVENLABS_AGENT_ID in .env")
            print("   - Get credentials from: https://elevenlabs.io/app")
        if not redis_ok:
            print("   - Start Redis server: redis-server")
            print("   - Install Redis: choco install redis-64")
        return 1


if __name__ == '__main__':
    sys.exit(main())
