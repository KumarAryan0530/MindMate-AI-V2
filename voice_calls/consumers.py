"""
WebSocket Consumer for handling real-time audio streaming between Twilio and ElevenLabs
"""
import json
import asyncio
import websockets
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import VoiceCallHistory
from .services.elevenlabs_service import ElevenLabsService

logger = logging.getLogger(__name__)


class MediaStreamConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for Twilio media streams"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.schedule_id = self.scope['url_route']['kwargs']['schedule_id']
        self.stream_sid = None
        self.call_sid = None
        self.elevenlabs_ws = None
        self.custom_parameters = {}
        self.user_transcript = []
        self.agent_responses = []
        self.is_connected = False
        
        await self.accept()
        logger.info(f"Twilio connected to media stream for schedule {self.schedule_id}")
        
        # Don't setup ElevenLabs yet - wait for stream to start
        # This will be done when we receive the 'start' event from Twilio
    
    async def setup_elevenlabs(self):
        """Connect to ElevenLabs WebSocket"""
        try:
            service = ElevenLabsService()
            signed_url = await database_sync_to_async(service.get_signed_url)()
            
            logger.info(f"Attempting to connect to ElevenLabs with URL: {signed_url[:50]}...")
            
            # Connect to ElevenLabs with timeout
            self.elevenlabs_ws = await asyncio.wait_for(
                websockets.connect(
                    signed_url,
                    ping_interval=20,
                    ping_timeout=10,
                    close_timeout=10
                ),
                timeout=15.0
            )
            self.is_connected = True
            logger.info("✓ Connected to ElevenLabs successfully")
            
            # Start listening to ElevenLabs
            asyncio.create_task(self.elevenlabs_listener())
            
        except asyncio.TimeoutError:
            logger.error("✗ Timeout connecting to ElevenLabs (15s)")
            self.is_connected = False
            raise
        except websockets.exceptions.InvalidURI as e:
            logger.error(f"✗ Invalid ElevenLabs WebSocket URI: {e}")
            self.is_connected = False
            raise
        except Exception as e:
            logger.error(f"✗ Failed to setup ElevenLabs: {type(e).__name__}: {e}")
            self.is_connected = False
            raise
    
    async def elevenlabs_listener(self):
        """Listen for messages from ElevenLabs"""
        if not self.elevenlabs_ws:
            logger.error("ElevenLabs WebSocket not initialized")
            return
            
        try:
            async for message in self.elevenlabs_ws:
                data = json.loads(message)
                await self.handle_elevenlabs_message(data)
        except websockets.exceptions.ConnectionClosed:
            logger.info("ElevenLabs connection closed")
            self.is_connected = False
        except Exception as e:
            logger.error(f"ElevenLabs listener error: {e}")
            self.is_connected = False
    
    async def handle_elevenlabs_message(self, message):
        """Handle messages from ElevenLabs Conversational AI"""
        msg_type = message.get('type')
        
        if msg_type == 'conversation_initiation_metadata':
            logger.info("ElevenLabs conversation initiated")
            # Log the conversation ID for tracking
            conv_id = message.get('conversation_initiation_metadata_event', {}).get('conversation_id')
            if conv_id:
                logger.info(f"Conversation ID: {conv_id}")
        
        elif msg_type == 'audio':
            # Forward audio from ElevenLabs to Twilio
            if self.stream_sid:
                # ElevenLabs sends audio in base64 format
                audio_chunk = message.get('audio_event', {}).get('audio_base_64')
                
                if audio_chunk:
                    await self.send(text_data=json.dumps({
                        'event': 'media',
                        'streamSid': self.stream_sid,
                        'media': {'payload': audio_chunk}
                    }))
        
        elif msg_type == 'interruption':
            # User interrupted the agent - clear Twilio's audio buffer
            if self.stream_sid:
                await self.send(text_data=json.dumps({
                    'event': 'clear',
                    'streamSid': self.stream_sid
                }))
                logger.info("User interrupted - cleared audio buffer")
        
        elif msg_type == 'ping':
            # Respond to keepalive ping from ElevenLabs
            event_id = message.get('ping_event', {}).get('event_id')
            if event_id and self.elevenlabs_ws and self.is_connected:
                try:
                    await self.elevenlabs_ws.send(json.dumps({
                        'type': 'pong',
                        'event_id': event_id
                    }))
                except Exception as e:
                    logger.error(f"Failed to send pong: {e}")
        
        elif msg_type == 'user_transcript':
            # User's speech transcribed
            user_text = message.get('user_transcription_event', {}).get('user_transcript', '')
            if user_text:
                self.user_transcript.append(user_text)
                logger.info(f"User said: {user_text}")
        
        elif msg_type == 'agent_response':
            # Agent's response text
            agent_text = message.get('agent_response_event', {}).get('agent_response', '')
            if agent_text:
                self.agent_responses.append(agent_text)
                logger.info(f"Agent said: {agent_text}")
        
        elif msg_type == 'internal_tentative_agent_response':
            # Agent is thinking/processing
            pass
        
        elif msg_type == 'error':
            # Error from ElevenLabs
            error_msg = message.get('error', {})
            logger.error(f"ElevenLabs error: {error_msg}")
        
        else:
            # Log unknown message types for debugging
            logger.debug(f"Unknown ElevenLabs message type: {msg_type}")
    
    async def receive(self, text_data=None, bytes_data=None):
        """Receive messages from Twilio"""
        try:
            if not text_data:
                return
                
            message = json.loads(text_data)
            event = message.get('event')
            
            if event == 'start':
                self.stream_sid = message['start']['streamSid']
                self.call_sid = message['start']['callSid']
                self.custom_parameters = message['start'].get('customParameters', {})
                
                logger.info(f"Stream started: {self.stream_sid}, Call: {self.call_sid}")
                
                # Now setup ElevenLabs connection
                try:
                    await self.setup_elevenlabs()
                    
                    # Send initial configuration to ElevenLabs
                    if self.elevenlabs_ws and self.is_connected:
                        service = ElevenLabsService()
                        config = service.create_agent_config(
                            self.custom_parameters.get('prompt'),
                            self.custom_parameters.get('first_message')
                        )
                        await self.elevenlabs_ws.send(json.dumps(config))
                        logger.info("Sent initial config to ElevenLabs")
                except Exception as e:
                    logger.error(f"Failed to setup ElevenLabs: {e}")
            
            elif event == 'media':
                # Forward audio from Twilio to ElevenLabs
                if self.elevenlabs_ws and self.is_connected:
                    try:
                        # Twilio sends audio in mulaw format, base64 encoded
                        payload = message['media']['payload']
                        
                        # ElevenLabs expects audio in specific format
                        audio_message = {
                            'user_audio_chunk': payload
                        }
                        await self.elevenlabs_ws.send(json.dumps(audio_message))
                    except Exception as e:
                        logger.error(f"Error forwarding audio to ElevenLabs: {e}")
            
            elif event == 'stop':
                logger.info(f"Stream {self.stream_sid} ended")
                await self.save_transcripts()
                await self.cleanup()
        
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
    
    async def disconnect(self, code):
        """Handle disconnect"""
        logger.info(f"Twilio disconnected with code: {code}")
        await self.save_transcripts()
        await self.cleanup()
    
    async def cleanup(self):
        """Cleanup connections"""
        self.is_connected = False
        if self.elevenlabs_ws:
            try:
                await self.elevenlabs_ws.close()
                logger.info("ElevenLabs WebSocket closed")
            except Exception as e:
                logger.error(f"Error closing ElevenLabs WebSocket: {e}")
            self.elevenlabs_ws = None
    
    @database_sync_to_async
    def save_transcripts(self):
        """Save conversation transcripts to database"""
        try:
            if self.call_sid:
                call_history = VoiceCallHistory.objects.filter(
                    twilio_call_sid=self.call_sid
                ).first()
                
                if call_history:
                    call_history.user_transcript = ' '.join(self.user_transcript)
                    call_history.agent_responses = ' '.join(self.agent_responses)
                    call_history.full_transcript = {
                        'user': self.user_transcript,
                        'agent': self.agent_responses
                    }
                    call_history.save()
                    logger.info(f"Transcripts saved for call {self.call_sid}")
        except Exception as e:
            logger.error(f"Failed to save transcripts: {e}")
