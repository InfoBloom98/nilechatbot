import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set default port or use environment variable
PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")

if __name__ == "__main__":
    print(f"Starting Nile University Chatbot API on {HOST}:{PORT}")
    print("Documentation available at: http://localhost:{PORT}/docs")
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True) 