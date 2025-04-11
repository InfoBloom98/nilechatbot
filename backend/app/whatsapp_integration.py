import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables for API keys
load_dotenv()

class WhatsAppHandler:
    def __init__(self, chatbot_engine):
        """Initialize WhatsApp handler"""
        self.chatbot_engine = chatbot_engine
        self.api_key = os.getenv("WHATSAPP_API_KEY", "")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
        self.api_url = "https://graph.facebook.com/v17.0"
        self.active = bool(self.api_key and self.phone_number_id)
        
        # Create a session mapping from WhatsApp numbers to chatbot session IDs
        self.session_map = {}
    
    def handle_incoming_message(self, sender_id, message_text):
        """Process incoming WhatsApp message and send response"""
        if not self.active:
            return {"error": "WhatsApp integration not configured"}
        
        # Get or create session ID for this sender
        if sender_id not in self.session_map:
            self.session_map[sender_id] = self.chatbot_engine.get_session_id()
        
        session_id = self.session_map[sender_id]
        
        # Process the message
        response, confidence, category = self.chatbot_engine.process_query(
            message_text, 
            session_id=session_id
        )
        
        # Send response back via WhatsApp
        self.send_message(sender_id, response)
        
        return {
            "status": "success", 
            "response": response, 
            "confidence": confidence,
            "category": category
        }
    
    def send_message(self, recipient_id, message_text):
        """Send a message via WhatsApp Cloud API"""
        if not self.active:
            return {"error": "WhatsApp integration not configured"}
        
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_id,
            "type": "text",
            "text": {
                "body": message_text
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def verify_webhook(self, mode, token, challenge):
        """Verify the webhook for WhatsApp Cloud API"""
        verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
        
        if mode and token and mode == "subscribe" and token == verify_token:
            return {"challenge": challenge}
        else:
            return {"error": "Verification failed"}, 403
    
    def setup_dotenv_file(self):
        """Create a .env template file for WhatsApp API credentials"""
        env_path = Path(__file__).parent.parent / '.env'
        
        if not env_path.exists():
            with open(env_path, 'w') as f:
                f.write("""# WhatsApp API credentials
WHATSAPP_API_KEY=your_whatsapp_api_key
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_VERIFY_TOKEN=your_webhook_verify_token
"""
                )
            return True
        return False 