import uuid
from datetime import datetime
import json
from pathlib import Path

class ChatbotEngine:
    def __init__(self, nlp_processor):
        self.nlp_processor = nlp_processor
        self.active_sessions = {}
        self.conversation_log_path = Path(__file__).parent.parent / 'data' / 'conversation_logs'
        self.conversation_log_path.mkdir(parents=True, exist_ok=True)
        
        # Default responses for each category
        self.default_responses = {
            "unknown": "I'm not sure I understand your question. Could you please rephrase it?",
            "fees_and_payments": "I have information about tuition fees, payment methods, and financial aid. What specifically would you like to know?",
            "hostel_and_accommodation": "I can assist with information about hostel availability, costs, and application process. What would you like to know?",
            "courses_and_academics": "I can help with information about programs, course registration, schedules, and academic matters. What do you need?",
            "university_calendar": "I can provide information about academic dates, exam schedules, and important events. What are you looking for?",
            "departments_and_faculties": "I can tell you about the departments and faculties at Nile University. What would you like to know?",
            "university_administration": "I can provide information about university officials and administrative offices. What would you like to know?",
            "student_services": "I can help with information about library services, IT support, and other student services. What do you need?",
            "general_information": "I have general information about Nile University. What would you like to know?"
        }
        
        # Load sample data to knowledge base
        self._load_sample_data()
    
    def _load_sample_data(self):
        """Load sample data to knowledge base if it's empty"""
        if not any(self.nlp_processor.knowledge_base.values()):
            # Fees and payments
            self.nlp_processor.add_to_knowledge_base(
                "fees_and_payments",
                "What are the tuition fees for undergraduate programs?",
                "Undergraduate program fees at Nile University vary by program but generally range from ₦2,000,000 to ₦3,500,000 per academic year.",
                ["How much is undergraduate tuition?", "What's the cost of undergraduate programs?"]
            )
            
            self.nlp_processor.add_to_knowledge_base(
                "fees_and_payments",
                "What are the payment methods available?",
                "You can pay your fees through bank transfer, online payment portal, or direct deposit at the university's bank. Visit the bursary for more details.",
                ["How can I pay my fees?", "What payment options are available?"]
            )
            
            # Hostel and accommodation
            self.nlp_processor.add_to_knowledge_base(
                "hostel_and_accommodation",
                "How much is hostel accommodation?",
                "Hostel fees range from ₦350,000 to ₦550,000 per academic year depending on the type of accommodation (shared or single room).",
                ["What's the cost of staying in the hostel?", "How much do I need to pay for accommodation?"]
            )
            
            # Courses and academics
            self.nlp_processor.add_to_knowledge_base(
                "courses_and_academics",
                "How do I register for courses?",
                "Course registration is done online through the student portal. Log in with your credentials, select the semester, and choose your courses based on your program requirements.",
                ["Course registration process", "How to register courses"]
            )
            
            # University calendar
            self.nlp_processor.add_to_knowledge_base(
                "university_calendar",
                "When does the academic year start?",
                "The academic year typically starts in late September or early October. The exact date for the current year can be found on the university website.",
                ["Starting date of academic session", "When do classes begin?"]
            )
            
            # Departments and faculties
            self.nlp_processor.add_to_knowledge_base(
                "departments_and_faculties",
                "What faculties are available at Nile University?",
                "Nile University has several faculties including Faculty of Engineering, Faculty of Arts and Social Sciences, Faculty of Management Sciences, Faculty of Natural and Applied Sciences, Faculty of Law, and Faculty of Health Sciences.",
                ["List of faculties", "What are the faculties in Nile University?"]
            )
            
            # University administration
            self.nlp_processor.add_to_knowledge_base(
                "university_administration",
                "Who is the Vice-Chancellor of Nile University?",
                "Please refer to the university website for the current Vice-Chancellor, as this information may change. The VC's office is located in the administration building.",
                ["Current Vice-Chancellor", "Name of the VC"]
            )
            
            # Student services
            self.nlp_processor.add_to_knowledge_base(
                "student_services",
                "How do I access the library resources?",
                "You can access the library with your student ID card. Electronic resources are available through the e-library portal accessible via the university website.",
                ["Library access", "How to use library resources"]
            )
    
    def get_session_id(self):
        """Generate a new session ID"""
        return str(uuid.uuid4())
    
    def process_query(self, query, session_id=None):
        """Process user query and return appropriate response"""
        # Create or retrieve session
        if not session_id:
            session_id = self.get_session_id()
        
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {
                "conversation": [],
                "start_time": datetime.now().isoformat()
            }
        
        # Get response from NLP processor
        response, confidence, category = self.nlp_processor.find_best_match(query)
        
        # Log conversation
        self.active_sessions[session_id]["conversation"].append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response,
            "confidence": float(confidence),
            "category": category
        })
        
        # Save conversation to log file
        self._save_conversation_log(session_id)
        
        return response, float(confidence), category
    
    def _save_conversation_log(self, session_id):
        """Save conversation to log file"""
        if session_id in self.active_sessions:
            log_file = self.conversation_log_path / f"{session_id}.json"
            with open(log_file, 'w') as f:
                json.dump(self.active_sessions[session_id], f, indent=4)
    
    def end_session(self, session_id):
        """End a chat session"""
        if session_id in self.active_sessions:
            # Record end time
            self.active_sessions[session_id]["end_time"] = datetime.now().isoformat()
            
            # Save final conversation log
            self._save_conversation_log(session_id)
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            return True
        return False 