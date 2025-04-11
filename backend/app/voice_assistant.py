import pyttsx3
import base64
import io
import tempfile
import os

class VoiceProcessor:
    def __init__(self):
        """Initialize the voice processor"""
        try:
            self.engine = pyttsx3.init()
            # Set properties
            self.engine.setProperty('rate', 150)  # Speed of speech
            self.engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
            
            # Get available voices
            voices = self.engine.getProperty('voices')
            if voices:
                # Try to find a female voice
                female_voice = next((voice for voice in voices if 'female' in voice.name.lower()), None)
                if female_voice:
                    self.engine.setProperty('voice', female_voice.id)
                else:
                    # Default to the first voice
                    self.engine.setProperty('voice', voices[0].id)
            
            self.available = True
        except Exception as e:
            print(f"Error initializing voice engine: {e}")
            self.available = False
    
    def text_to_speech(self, text):
        """Convert text to speech and return as base64 encoded audio"""
        if not self.available:
            return None
        
        try:
            # Create a temp file to save the audio
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_filename = temp_file.name
            
            # Use pyttsx3 to save audio to file
            self.engine.save_to_file(text, temp_filename)
            self.engine.runAndWait()
            
            # Read the file and encode to base64
            with open(temp_filename, 'rb') as audio_file:
                audio_data = audio_file.read()
                base64_audio = base64.b64encode(audio_data).decode('utf-8')
            
            # Clean up the temp file
            os.remove(temp_filename)
            
            return base64_audio
        except Exception as e:
            print(f"Error in text-to-speech conversion: {e}")
            return None
    
    def speak_text(self, text):
        """Speak the text out loud (for local testing)"""
        if not self.available:
            return False
        
        try:
            self.engine.say(text)
            self.engine.runAndWait()
            return True
        except Exception as e:
            print(f"Error speaking text: {e}")
            return False 