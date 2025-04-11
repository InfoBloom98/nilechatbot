import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import json
import os
from pathlib import Path
import numpy as np

class NLPProcessor:
    def __init__(self):
        # Download required NLTK resources
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')
        
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        # Use ngram_range to capture phrases, increase max_features for more vocabulary
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 3), max_features=5000)
        
        # Load knowledge base
        self.kb_path = Path(__file__).parent.parent / 'data' / 'knowledge_base.json'
        self.knowledge_base = self._load_knowledge_base()
        
        # Prepare vectorized corpus
        self.corpus = []
        self.kb_responses = []
        self.kb_categories = []
        self.original_questions = []  # Store original questions for exact match checking
        
        for category, items in self.knowledge_base.items():
            for item in items:
                for question in item["questions"]:
                    self.corpus.append(question)
                    self.kb_responses.append(item["answer"])
                    self.kb_categories.append(category)
                    self.original_questions.append(question.lower())  # Store lowercase for comparison
        
        if self.corpus:  # Only fit if corpus is not empty
            self.X = self.vectorizer.fit_transform(self.corpus)
    
    def _load_knowledge_base(self):
        """Load knowledge base from JSON file or create if not exists"""
        if not self.kb_path.exists():
            # Create directory if it doesn't exist
            self.kb_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create basic knowledge base structure
            knowledge_base = {
                "fees_and_payments": [],
                "hostel_and_accommodation": [],
                "courses_and_academics": [],
                "university_calendar": [],
                "departments_and_faculties": [],
                "university_administration": [],
                "student_services": [],
                "general_information": []
            }
            
            # Add some default data
            knowledge_base["general_information"].append({
                "questions": [
                    "What is Nile University?",
                    "Tell me about Nile University",
                    "Give me information about Nile University"
                ],
                "answer": "Nile University is a private university located in Abuja, Nigeria, dedicated to excellence in teaching, research, and service to the community."
            })
            
            # Save knowledge base to file
            with open(self.kb_path, 'w') as f:
                json.dump(knowledge_base, f, indent=4)
            
            return knowledge_base
        else:
            try:
                with open(self.kb_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                # Handle corrupted file
                return {
                    "fees_and_payments": [],
                    "hostel_and_accommodation": [],
                    "courses_and_academics": [],
                    "university_calendar": [],
                    "departments_and_faculties": [],
                    "university_administration": [],
                    "student_services": [],
                    "general_information": []
                }
    
    def preprocess_text(self, text):
        """Preprocess text by tokenizing, removing stopwords and lemmatizing"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        processed_tokens = [
            self.lemmatizer.lemmatize(token) 
            for token in tokens 
            if token not in self.stop_words
        ]
        
        return ' '.join(processed_tokens)
    
    def find_best_match(self, query):
        """Find the best match for the query in the knowledge base"""
        if not self.corpus:
            return "I don't have any information yet.", 0.0, "general_information"
        
        # Check for exact match first (case-insensitive)
        query_lower = query.lower().strip()
        
        # First check for exact matches
        for i, original_question in enumerate(self.original_questions):
            if query_lower == original_question:
                # Exact match found, return with confidence 1.0
                return self.kb_responses[i], 1.0, self.kb_categories[i]
        
        # Next, look for questions that contain the query as a substring
        matching_indices = []
        for i, original_question in enumerate(self.original_questions):
            if query_lower in original_question or original_question in query_lower:
                matching_indices.append((i, len(original_question)))
        
        # If we found substring matches, return the longest one (most specific)
        if matching_indices:
            # Sort by length of question (descending)
            matching_indices.sort(key=lambda x: x[1], reverse=True)
            best_idx = matching_indices[0][0]
            # Higher confidence for substring matches (0.85-0.95)
            confidence = min(0.95, 0.85 + (len(query_lower) / len(self.original_questions[best_idx])) * 0.1)
            return self.kb_responses[best_idx], confidence, self.kb_categories[best_idx]
        
        # If no direct matches, proceed with vector similarity
        # Preprocess the query
        processed_query = self.preprocess_text(query)
        
        # Vectorize the query
        query_vec = self.vectorizer.transform([processed_query])
        
        # Calculate similarity
        similarities = cosine_similarity(query_vec, self.X).flatten()
        
        # Find the index of the best match
        best_match_index = similarities.argmax()
        confidence = similarities[best_match_index]
        
        # Boost confidence for higher similarity scores
        if confidence > 0.7:
            confidence = min(0.98, confidence + 0.15)
        elif confidence > 0.5:
            confidence = min(0.9, confidence + 0.1)
        elif confidence > 0.3:
            confidence = min(0.85, confidence + 0.05)
        
        if confidence < 0.3:  # Threshold for confidence
            return "I'm not sure how to answer that. Please try rephrasing your question.", confidence, "unknown"
        
        return self.kb_responses[best_match_index], confidence, self.kb_categories[best_match_index]
    
    def add_to_knowledge_base(self, category, question, answer, related_questions=None):
        """Add new entry to knowledge base"""
        if category not in self.knowledge_base:
            self.knowledge_base[category] = []
        
        questions = [question]
        if related_questions:
            questions.extend(related_questions)
        
        # Check if answer already exists
        for item in self.knowledge_base[category]:
            if item["answer"] == answer:
                # Update questions for existing answer
                item["questions"].extend([q for q in questions if q not in item["questions"]])
                break
        else:
            # Add new entry
            self.knowledge_base[category].append({
                "questions": questions,
                "answer": answer
            })
        
        # Update corpus and vectorizer
        self.corpus = []
        self.kb_responses = []
        self.kb_categories = []
        self.original_questions = []
        
        for cat, items in self.knowledge_base.items():
            for item in items:
                for q in item["questions"]:
                    self.corpus.append(q)
                    self.kb_responses.append(item["answer"])
                    self.kb_categories.append(cat)
                    self.original_questions.append(q.lower())
        
        if self.corpus:  # Only fit if corpus is not empty
            self.X = self.vectorizer.fit_transform(self.corpus)
        
        # Save updated knowledge base
        with open(self.kb_path, 'w') as f:
            json.dump(self.knowledge_base, f, indent=4)
        
        return True 