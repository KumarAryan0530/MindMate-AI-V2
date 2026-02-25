"""
Test script for ElevenLabs and Twilio integration
Run this before starting voice calls to verify everything is configured correctly
"""
import os
import sys
import django
import asyncio
import websockets

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'perplex.settings')
django.setup()

from django.conf import settings
from voice_calls.services.elevenlabs_service import ElevenLabsService
from voice_calls.services.twilio_service import TwilioService


def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def check_env_vars():
    """Check if all required environment variables are set"""
    print_header("Checking Environment Variables")
    
    required_vars = {
        'TWILIO_ACCOUNT_SID': settings.TWILIO_ACCOUNT_SID,
        'TWILIO_AUTH_TOKEN': settings.TWILIO_AUTH_TOKEN,
        'TWILIO_PHONE_NUMBER': settings.TWILIO_PHONE_NUMBER,
        'ELEVENLABS_API_KEY': settings.ELEVENLABS_API_KEY,
        'ELEVENLABS_AGENT_ID': settings.ELEVENLABS_AGENT_ID,
        'NGROK_URL': settings.NGROK_URL,
    }
    
    all_set = True
    for var_name, var_value in required_vars.items():
        if var_value:
            print(f"✓ {var_name}: {'*' * 10}...{var_value[-4:] if len(var_value) > 4 else '****'}")
        else:
            print(f"✗ {var_name}: NOT SET")
            all_set = False
    
    return all_set


def test_twilio_connection():
    """Test Twilio API connection"""
    print_header("Testing Twilio Connection")
    
    try:
        service = TwilioService()
        # Try to fetch account info
        account = service.client.api.accounts(settings.TWILIO_ACCOUNT_SID).fetch()
        print(f"✓ Twilio connection successful")
        print(f"  Account SID: {account.sid}")
        print(f"  Account Status: {account.status}")
        print(f"  Type: {account.type}")
        
        if account.type == 'Trial':
            print(f"\n⚠️  WARNING: This is a TRIAL account")
            print(f"  Trial accounts have limitations:")
            print(f"  - Can only call verified phone numbers")
            print(f"  - Plays 'press any key' message before your app")
            print(f"  - Limited features")
            print(f"\n  To verify phone numbers:")
            print(f"  https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
        
        return True
    except Exception as e:
        print(f"✗ Twilio connection failed: {e}")
        return False


async def test_elevenlabs_connection():
    """Test ElevenLabs connection"""
    print_header("Testing ElevenLabs Connection")
    
    try:
        service = ElevenLabsService()
        print(f"  Getting signed URL...")
        signed_url = service.get_signed_url()
        print(f"✓ Got signed URL: {signed_url[:60]}...")
        
        print(f"  Attempting WebSocket connection...")
        async with websockets.connect(
            signed_url,
            ping_interval=20,
            ping_timeout=10,
            close_timeout=10
        ) as ws:
            print(f"✓ WebSocket connection established")
            
            # Send a test initialization message
            config = service.create_agent_config()
            await ws.send(str(config))
            print(f"✓ Sent agent configuration")
            
            # Try to receive a message (with timeout)
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                print(f"✓ Received response from ElevenLabs")
                return True
            except asyncio.TimeoutError:
                print(f"⚠️  No immediate response (this is normal)")
                return True
            
    except websockets.exceptions.InvalidURI as e:
        print(f"✗ Invalid WebSocket URI: {e}")
        print(f"  Check your ELEVENLABS_API_KEY and ELEVENLABS_AGENT_ID")
        return False
    except Exception as e:
        print(f"✗ ElevenLabs connection failed: {type(e).__name__}: {e}")
        return False


def test_ngrok():
    """Test if ngrok URL is accessible"""
    print_header("Testing Ngrok Configuration")
    
    if not settings.NGROK_URL:
        print(f"✗ NGROK_URL not set in .env file")
        return False
    
    print(f"  Ngrok URL: {settings.NGROK_URL}")
    
    # Check if it's a valid URL
    if not settings.NGROK_URL.startswith('http'):
        print(f"✗ NGROK_URL should start with https://")
        return False
    
    print(f"✓ NGROK_URL format looks correct")
    print(f"\n  Make sure:")
    print(f"  1. Ngrok is running: ngrok http 8000")
    print(f"  2. NGROK_URL matches the current ngrok session")
    print(f"  3. Daphne server is running on port 8000")
    
    return True


def check_ports():
    """Check if required ports are available"""
    print_header("Checking Port Status")
    
    import socket
    
    ports_to_check = {
        8000: 'Daphne/Django server',
        6379: 'Redis',
    }
    
    for port, service in ports_to_check.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:
            print(f"✓ Port {port} is in use ({service})")
        else:
            print(f"✗ Port {port} is NOT in use ({service} not running?)")


def main():
    """Run all diagnostic tests"""
    print("\n" + "="*60)
    print("  MindMate-AI Voice Calls - Diagnostic Test")
    print("="*60)
    
    # Check environment variables
    if not check_env_vars():
        print("\n⚠️  Some environment variables are missing!")
        print("Please set all required variables in your .env file")
        return
    
    # Check ports
    check_ports()
    
    # Test Twilio
    twilio_ok = test_twilio_connection()
    
    # Test ElevenLabs
    elevenlabs_ok = asyncio.run(test_elevenlabs_connection())
    
    # Test Ngrok
    ngrok_ok = test_ngrok()
    
    # Final summary
    print_header("Diagnostic Summary")
    
    print(f"Environment Variables: {'✓ PASS' if True else '✗ FAIL'}")
    print(f"Twilio Connection:     {'✓ PASS' if twilio_ok else '✗ FAIL'}")
    print(f"ElevenLabs Connection: {'✓ PASS' if elevenlabs_ok else '✗ FAIL'}")
    print(f"Ngrok Configuration:   {'✓ PASS' if ngrok_ok else '✗ FAIL'}")
    
    if twilio_ok and elevenlabs_ok and ngrok_ok:
        print("\n🎉 All tests passed! You're ready to make voice calls.")
        print("\nNext steps:")
        print("1. Make sure these services are running:")
        print("   - Daphne server (port 8000)")
        print("   - Celery worker")
        print("   - Celery beat")
        print("   - Ngrok")
        print("   - Redis")
        print("\n2. Go to http://localhost:8000/voice/schedule/")
        print("3. Click 'Call Now' or 'Schedule Later'")
        print("4. Answer your phone and enjoy the AI conversation!")
    else:
        print("\n❌ Some tests failed. Please fix the issues above before proceeding.")
        print("\nCommon fixes:")
        print("- Make sure all API keys are correct in .env file")
        print("- Restart ngrok and update NGROK_URL in .env")
        print("- Check your internet connection")
        print("- Verify your Twilio account status")
    
    print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    main()
