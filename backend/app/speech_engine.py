import speech_recognition as sr
import pyttsx3
import io
import base64
import tempfile
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("speech_engine")

class SpeechEngine:
    def __init__(self):
        logger.info("Initializing SpeechEngine")
        self.recognizer = sr.Recognizer()
        
        # Configure recognizer settings for better recognition
        self.recognizer.energy_threshold = 300  # Increase for noisy environments
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8  # Time of silence before considering the phrase complete
        
        # Initialize TTS engine
        try:
            self.engine = pyttsx3.init()
            
            # Set voice properties
            self.engine.setProperty('rate', 150)  # Speed of speech
            self.engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
            
            # Get available voices and set a female voice if available
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if 'female' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    logger.info(f"Using voice: {voice.name}")
                    break
            logger.info("Text-to-speech engine initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing text-to-speech engine: {str(e)}")
            self.engine = None
    
    def speech_to_text(self, audio_data):
        """Convert speech audio to text using Google's Speech Recognition API"""
        logger.info("Starting speech-to-text conversion")
        
        if not audio_data:
            logger.error("No audio data received")
            return "Sorry, I didn't receive any audio data."
        
        temp_audio_path = None
        try:
            # Decode base64 audio data
            logger.info(f"Decoding base64 audio data (length: {len(audio_data)})")
            audio_bytes = base64.b64decode(audio_data)
            logger.info(f"Decoded audio size: {len(audio_bytes)} bytes")
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
                temp_audio.write(audio_bytes)
                temp_audio_path = temp_audio.name
                logger.info(f"Audio saved to temporary file: {temp_audio_path}")
            
            # Recognize speech using the temporary file
            logger.info("Starting speech recognition")
            with sr.AudioFile(temp_audio_path) as source:
                logger.info("Recording audio from file")
                audio = self.recognizer.record(source)
                logger.info("Recognizing speech")
                text = self.recognizer.recognize_google(audio)
                logger.info(f"Speech recognized: '{text}'")
                return text
        except sr.UnknownValueError:
            logger.warning("Speech recognition could not understand audio")
            return "Sorry, I couldn't understand what you said."
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {str(e)}")
            return "Sorry, my speech recognition service is unavailable at the moment."
        except Exception as e:
            logger.error(f"Error in speech recognition: {str(e)}")
            return "An error occurred during speech recognition."
        finally:
            # Clean up temp file
            if temp_audio_path and os.path.exists(temp_audio_path):
                try:
                    os.remove(temp_audio_path)
                    logger.info(f"Temporary file removed: {temp_audio_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove temporary file: {str(e)}")
    
    def text_to_speech(self, text):
        """Convert text to speech and return as base64 encoded string"""
        logger.info(f"Converting text to speech: '{text}'")
        
        if not self.engine:
            logger.error("TTS engine not initialized")
            return None
            
        temp_audio_path = None
        try:
            # Create a temporary file to store the audio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
                temp_audio_path = temp_audio.name
                logger.info(f"Created temporary file for audio: {temp_audio_path}")
            
            # Save speech to the temporary file
            logger.info("Generating speech audio")
            self.engine.save_to_file(text, temp_audio_path)
            self.engine.runAndWait()
            
            # Read the audio file and encode to base64
            logger.info("Reading audio file and encoding to base64")
            with open(temp_audio_path, 'rb') as audio_file:
                audio_data = audio_file.read()
                base64_audio = base64.b64encode(audio_data).decode('utf-8')
                logger.info(f"Base64 audio length: {len(base64_audio)}")
            
            return base64_audio
        except Exception as e:
            logger.error(f"Error in text-to-speech conversion: {str(e)}")
            return None
        finally:
            # Clean up temp file
            if temp_audio_path and os.path.exists(temp_audio_path):
                try:
                    os.remove(temp_audio_path)
                    logger.info(f"Temporary file removed: {temp_audio_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove temporary file: {str(e)}") 