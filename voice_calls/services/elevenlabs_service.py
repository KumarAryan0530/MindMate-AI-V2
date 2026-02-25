"""
ElevenLabs Service for AI-powered voice conversations
"""
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class ElevenLabsService:
    """Service class for ElevenLabs API interactions"""
    
    def __init__(self):
        """Initialize ElevenLabs service with API credentials"""
        self.api_key = settings.ELEVENLABS_API_KEY
        self.agent_id = settings.ELEVENLABS_AGENT_ID
        self.base_url = "https://api.elevenlabs.io/v1"
    
    def get_signed_url(self):
        """
        Get signed WebSocket URL for conversation
        
        Returns:
            str: Signed WebSocket URL for ElevenLabs connection
            
        Raises:
            Exception: If URL generation fails
        """
        try:
            url = f"{self.base_url}/convai/conversation/get_signed_url"
            params = {'agent_id': self.agent_id}
            headers = {'xi-api-key': self.api_key}
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            signed_url = data.get('signed_url')
            
            if not signed_url:
                raise ValueError("No signed URL in response")
            
            logger.info("Successfully obtained ElevenLabs signed URL")
            return signed_url
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get signed URL from ElevenLabs: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting signed URL: {e}")
            raise
    
    def create_agent_config(self, custom_prompt=None, first_message=None):
        """
        Create agent configuration for conversation
        
        Args:
            custom_prompt (str): Custom prompt for the AI agent (only if agent allows override)
            first_message (str): First message - NOT USED (most agents don't allow override)
            
        Returns:
            dict: Agent configuration object for WebSocket initialization
        """
        # NOTE: Most ElevenLabs agents don't allow first_message override
        # The agent's configured first message will be used automatically
        # We only send an empty config to initiate the conversation
        
        # Send minimal config - let agent use its own configuration
        # Attempting to override first_message causes "policy violation" error
        config = {
            "type": "conversation_initiation_client_data",
        }
        
        logger.debug("Created minimal agent configuration (using agent's default settings)")
        return config
    
    def analyze_sentiment(self, transcript_text):
        """
        Analyze sentiment of conversation transcript using AI
        
        Args:
            transcript_text (str): The conversation transcript to analyze
            
        Returns:
            dict: Sentiment analysis results
        """
   
        
        try:
            # Simple keyword-based sentiment analysis as fallback
            positive_keywords = ['happy', 'good', 'great', 'better', 'fine', 'well', 'glad', 'joy']
            negative_keywords = ['sad', 'bad', 'depressed', 'anxious', 'worried', 'stress', 'difficult', 'hard']
            
            text_lower = transcript_text.lower()
            
            positive_count = sum(1 for word in positive_keywords if word in text_lower)
            negative_count = sum(1 for word in negative_keywords if word in text_lower)
            
            total_words = len(transcript_text.split())
            
            if total_words == 0:
                return {
                    'sentiment': 'neutral',
                    'positive_score': 0,
                    'negative_score': 0,
                    'neutral_score': 25,
                    'confidence': 0.0
                }
            
            # Calculate scores (0-25 scale)
            positive_score = min((positive_count / total_words) * 100, 25)
            negative_score = min((negative_count / total_words) * 100, 25)
            neutral_score = max(25 - positive_score - negative_score, 0)
            
            # Determine overall sentiment
            if positive_score > negative_score:
                sentiment = 'positive'
            elif negative_score > positive_score:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            confidence = min((positive_count + negative_count) / max(total_words / 10, 1), 1.0)
            
            return {
                'sentiment': sentiment,
                'positive_score': positive_score,
                'negative_score': negative_score,
                'neutral_score': neutral_score,
                'confidence': confidence,
                'emotions_detected': [],
                'key_phrases': []
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {
                'sentiment': 'neutral',
                'positive_score': 0,
                'negative_score': 0,
                'neutral_score': 25,
                'confidence': 0.0,
                'emotions_detected': [],
                'key_phrases': []
            }
    
    def test_connection(self):
        """
        Test connection to ElevenLabs API
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.get_signed_url()
            logger.info("ElevenLabs connection test successful")
            return True
        except Exception as e:
            logger.error(f"ElevenLabs connection test failed: {e}")
            return False
