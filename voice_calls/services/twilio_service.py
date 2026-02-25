"""
Twilio Service for managing voice calls
"""
from twilio.rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class TwilioService:
    """Service class for Twilio API interactions"""
    
    def __init__(self):
        """Initialize Twilio client with credentials from settings"""
        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        self.from_number = settings.TWILIO_PHONE_NUMBER
    
    def initiate_call(self, to_number, twiml_url):
        """
        Initiate an outbound call
        
        Args:
            to_number (str): Phone number to call (with country code)
            twiml_url (str): URL that returns TwiML instructions
            
        Returns:
            str: Twilio Call SID if successful
            
        Raises:
            Exception: If call initiation fails
        """
        try:
            call = self.client.calls.create(
                to=to_number,
                from_=self.from_number,
                url=twiml_url,
                method='POST',
                status_callback_method='POST',
                status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
                timeout=60,  # Ring for up to 60 seconds
                record=False  # Don't record the call
            )
            logger.info(f"Call initiated successfully: {call.sid} to {to_number}")
            return call.sid
        except Exception as e:
            logger.error(f"Failed to initiate call to {to_number}: {e}")
            raise
    
    def get_call_details(self, call_sid):
        """
        Retrieve call details from Twilio
        
        Args:
            call_sid (str): Twilio Call SID
            
        Returns:
            dict: Call details including duration, status, timestamps
            None: If call details cannot be retrieved
        """
        try:
            call = self.client.calls(call_sid).fetch()
            return {
                'duration': call.duration,
                'status': call.status,
                'start_time': call.start_time,
                'end_time': call.end_time,
                'direction': call.direction,
                'from_formatted': call.from_formatted,
                'to_formatted': call.to_formatted
            }
        except Exception as e:
            logger.error(f"Failed to fetch call details for {call_sid}: {e}")
            return None
    
    def get_call_status(self, call_sid):
        """
        Get current status of a call
        
        Args:
            call_sid (str): Twilio Call SID
            
        Returns:
            str: Call status (queued, ringing, in-progress, completed, etc.)
            None: If status cannot be retrieved
        """
        try:
            call = self.client.calls(call_sid).fetch()
            return call.status
        except Exception as e:
            logger.error(f"Failed to get call status for {call_sid}: {e}")
            return None
    
    def hang_up_call(self, call_sid):
        """
        Hang up an active call
        
        Args:
            call_sid (str): Twilio Call SID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.client.calls(call_sid).update(status='completed')
            logger.info(f"Call {call_sid} hung up successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to hang up call {call_sid}: {e}")
            return False
    
    def validate_phone_number(self, phone_number):
        """
        Validate phone number format using Twilio's Lookup API
        
        Args:
            phone_number (str): Phone number to validate
            
        Returns:
            dict: Validated phone number details
            None: If validation fails
        """
        try:
            # Use Twilio Lookup API to validate
            phone_info = self.client.lookups.v1.phone_numbers(phone_number).fetch()
            return {
                'valid': True,
                'formatted': phone_info.phone_number,
                'country_code': phone_info.country_code,
                'national_format': phone_info.national_format
            }
        except Exception as e:
            logger.warning(f"Phone number validation failed for {phone_number}: {e}")
            # Basic validation fallback
            if phone_number.startswith('+') and len(phone_number) >= 10:
                return {
                    'valid': True,
                    'formatted': phone_number,
                    'country_code': None,
                    'national_format': None
                }
            return None
