# Nile University Chatbot - Backend

This is the backend implementation for the Nile University Chatbot, designed to assist students with university-related queries.

## Features

- FastAPI REST API for chatbot interactions
- NLP-based query processing with NLTK
- Text-to-speech capability for voice responses
- WhatsApp integration for messaging
- Session management for conversation context
- Knowledge base with comprehensive university information

## Installation

1. Clone this repository
2. Create a Python virtual environment:

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix/MacOS
source venv/bin/activate
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables (optional for WhatsApp integration):
   - Create a `.env` file based on the template in the root directory
   - Add your WhatsApp API credentials

## Running the API

Start the FastAPI application with Uvicorn:

```bash
cd backend
uvicorn main:app --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000).

The API documentation (Swagger UI) will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

## API Endpoints

- `GET /` - Check API status
- `POST /api/chat` - Send a query to the chatbot
- `GET /api/categories` - Get available categories for queries

## Knowledge Base

The chatbot comes pre-loaded with sample data about Nile University, including:

- Fees and payment information
- Hostel and accommodation details
- Courses and academic procedures
- University calendar and important dates
- Department and faculty information
- University administration contacts
- Student services information
- General university information

You can extend or modify the knowledge base by editing the `data/knowledge_base.json` file.

## WhatsApp Integration

To enable WhatsApp integration:

1. Obtain API credentials from WhatsApp Business API
2. Add the credentials to your `.env` file
3. Restart the application

## Voice Assistant

The chatbot includes text-to-speech capability using pyttsx3. This feature is optional and can be triggered by setting `voice_response=True` in the API request. 