# Nile University Chatbot

A comprehensive chatbot designed for Nile University, Abuja, to assist students with university-related queries.

## Features

- Interactive web interface built with React
- FastAPI backend with NLP capabilities
- Voice assistant capability
- WhatsApp integration for messaging
- Comprehensive knowledge base covering:
  - Fees & Payments
  - Hostel & Accommodation
  - Courses & Academics
  - University Calendar
  - Departments & Faculties
  - University Administration
  - Student Services
  - General University Information

## Project Structure

```
nilechatbot/
├── backend/               # FastAPI backend
│   ├── app/               # Backend modules
│   ├── data/              # Knowledge base and logs
│   ├── requirements.txt   # Python dependencies
│   └── main.py            # FastAPI entry point
└── src/                   # React frontend
    ├── components/        # React components
    │   └── ChatInterface/ # Chat UI components
    ├── App.js             # Main React app
    └── index.js           # React entry point
```

## Installation & Setup

### Backend Setup

1. Navigate to the backend directory:

```bash
cd backend
```

2. Create a Python virtual environment:

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix/MacOS
source venv/bin/activate
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The backend API will be available at http://localhost:8000.

### Frontend Setup

1. Install Node.js dependencies:

```bash
npm install
```

2. Start the React development server:

```bash
npm start
```

The frontend will be available at http://localhost:3000.

## Usage

1. Open the web interface at http://localhost:3000 in your browser
2. Type your question in the chat input field
3. Toggle voice responses if desired
4. Receive accurate information about Nile University

## WhatsApp Integration

To enable WhatsApp integration:

1. Obtain WhatsApp Business API credentials
2. Add credentials to the `.env` file in the backend directory
3. Restart the backend server

## Development & Customization

### Extending the Knowledge Base

The chatbot's knowledge is stored in `backend/data/knowledge_base.json`. To add or update information:

1. Open the JSON file
2. Add new entries to the appropriate category
3. Restart the backend server to apply changes

### Customizing the UI

The frontend interface can be customized by modifying the React components in `src/components/`.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Nile University of Nigeria, Abuja
- FastAPI Framework
- React.js
