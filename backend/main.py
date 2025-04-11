import os
import logging
import time
from fastapi import FastAPI, HTTPException, Depends, Request, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel
import json
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("backend.log")
    ]
)
logger = logging.getLogger("backend")

# Import custom modules
from app.nlp_engine import NLPProcessor
from app.chatbot import ChatbotEngine
from app.voice_assistant import VoiceProcessor
from app.whatsapp_integration import WhatsAppHandler
from app.speech_engine import SpeechEngine

# Create instances of processors
logger.info("Initializing NLP and Speech processors")
nlp_processor = NLPProcessor()
chatbot_engine = ChatbotEngine(nlp_processor)
voice_processor = VoiceProcessor()
whatsapp_handler = WhatsAppHandler(chatbot_engine)
speech_engine = SpeechEngine()

# Create FastAPI app
app = FastAPI(
    title="Nile University Chatbot API",
    description="API for Nile University Chatbot serving students with university information",
    version="1.0.0"
)
logger.info("Starting FastAPI application")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define models
class ChatQuery(BaseModel):
    query: str
    session_id: str = None
    voice_response: bool = False

class VoiceQuery(BaseModel):
    audio_data: str  # Base64 encoded audio data
    session_id: str = None

# Session storage
sessions = {}

# API routes
@app.get("/")
async def root():
    return {"status": "active", "message": "Nile University Chatbot API is running"}

@app.post("/api/chat")
async def chat(request: ChatQuery):
    """Handle text chat requests"""
    logger.info(f"Received chat request: {request.query[:30]}...")
    
    try:
        # Generate session ID if not provided
        if not request.session_id:
            request.session_id = f"session_{time.time()}_{hash(request.query)}"
            logger.info(f"Generated session ID: {request.session_id}")
        
        # Get or create session
        if request.session_id not in sessions:
            sessions[request.session_id] = {
                "history": []
            }
            logger.info(f"Created new session: {request.session_id}")
        
        # Process query
        response, confidence, category = nlp_processor.find_best_match(request.query)
        logger.info(f"NLP response: '{response[:50]}...' (confidence: {confidence}, category: {category})")
        
        # Store in history
        sessions[request.session_id]["history"].append({
            "query": request.query,
            "response": response,
            "confidence": confidence,
            "category": category
        })
        
        # Generate voice response if requested
        voice_data = None
        if request.voice_response:
            logger.info("Generating voice response")
            voice_data = speech_engine.text_to_speech(response)
        
        return {
            "response": response,
            "confidence": float(confidence),
            "category": category,
            "voice_data": voice_data
        }
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/api/voice-chat")
async def voice_chat(request: VoiceQuery):
    """Handle voice chat requests"""
    logger.info("Received voice chat request")
    
    try:
        # Validate input
        if not request.audio_data:
            logger.error("No audio data received")
            raise HTTPException(status_code=400, detail="No audio data received")
        
        if not request.session_id:
            request.session_id = f"voice_session_{time.time()}"
            logger.info(f"Generated voice session ID: {request.session_id}")
        
        logger.info(f"Audio data length: {len(request.audio_data)}")
        
        # Convert speech to text
        text_query = speech_engine.speech_to_text(request.audio_data)
        logger.info(f"Recognized text: '{text_query}'")
        
        if not text_query or text_query.startswith("Sorry,"):
            # Return error response for failed recognition
            logger.warning(f"Speech recognition failed: {text_query}")
            return {
                "query": "",
                "response": text_query,
                "confidence": 0.0,
                "category": "error",
                "error": True
            }
        
        # Get or create session
        if request.session_id not in sessions:
            sessions[request.session_id] = {
                "history": []
            }
        
        # Process the text query
        response, confidence, category = nlp_processor.find_best_match(text_query)
        logger.info(f"NLP response: '{response[:50]}...' (confidence: {confidence}, category: {category})")
        
        # Store in history
        sessions[request.session_id]["history"].append({
            "query": text_query,
            "response": response,
            "confidence": confidence,
            "category": category
        })
        
        # Generate voice response
        logger.info("Generating voice response")
        voice_data = speech_engine.text_to_speech(response)
        
        return {
            "query": text_query,
            "response": response,
            "confidence": float(confidence),
            "category": category,
            "voice_data": voice_data
        }
    except Exception as e:
        logger.error(f"Error in voice chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing voice: {str(e)}")

@app.get("/api/categories")
async def get_categories():
    return {
        "categories": [
            "fees_and_payments",
            "hostel_and_accommodation",
            "courses_and_academics",
            "university_calendar",
            "departments_and_faculties",
            "university_administration",
            "student_services",
            "general_information"
        ]
    }

@app.post("/api/transcribe")
async def transcribe_audio(request: VoiceQuery):
    """Transcribe audio to text without generating a response"""
    logger.info("Received transcription request")
    
    try:
        # Validate input
        if not request.audio_data:
            logger.error("No audio data received")
            raise HTTPException(status_code=400, detail="No audio data received")
        
        # Generate session ID if not provided
        if not request.session_id:
            request.session_id = f"transcribe_{time.time()}"
            logger.info(f"Generated transcription session ID: {request.session_id}")
        
        logger.info(f"Audio data length: {len(request.audio_data)}")
        
        # Convert speech to text
        text = speech_engine.speech_to_text(request.audio_data)
        logger.info(f"Transcribed text: '{text}'")
        
        if not text or text.startswith("Sorry,"):
            # Return error response for failed transcription
            logger.warning(f"Transcription failed: {text}")
            return {
                "success": False,
                "text": "Sorry, I couldn't understand what you said.",
                "error": True
            }
        
        return {
            "success": True,
            "text": text
        }
    except Exception as e:
        logger.error(f"Error in transcription: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing voice: {str(e)}")

# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 