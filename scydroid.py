import os
import re
import json
import pickle
import random
import requests
import datetime
import numpy as np
import spacy
import nltk
import webbrowser
import speech_recognition as sr
import pyttsx3
import threading
import time
import logging
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

from nltk.corpus import wordnet
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder
from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering

# Ensure NLTK resources are downloaded
nltk.download('wordnet', quiet=True)
nltk.download('punkt', quiet=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='scydroid.log'
)
logger = logging.getLogger('ScyDroid')

class AdvancedScyDroidAI:
    def __init__(self):
        # Initialize threading for background operations
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.is_processing = False
        
        # Speech and Text Initialization with error handling
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            self.voice_options = voices
            if voices:
                self.engine.setProperty('voice', voices[1].id)  # Default to female voice if available
            self.engine.setProperty('rate', 175)  # Slightly faster default rate
        except Exception as e:
            logger.error(f"Text-to-speech initialization error: {e}")
            self.engine = None
            
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000  # Increased sensitivity
        self.recognizer.dynamic_energy_threshold = True

        # NLP Setup with fallback options
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except Exception as e:
            logger.warning(f"SpaCy model not loaded: {e}")
            try:
                os.system('python -m spacy download en_core_web_sm')
                self.nlp = spacy.load('en_core_web_sm')
            except:
                logger.error("Failed to download and load SpaCy model")
                self.nlp = None

        # Transformer Models with error handling
        try:
            logger.info("Loading transformer models...")
            self.sentiment_analyzer = pipeline('sentiment-analysis')
            self.zero_shot_classifier = pipeline('zero-shot-classification')
            
            # Add QA model for better responses
            self.tokenizer = AutoTokenizer.from_pretrained("distilbert-base-cased-distilled-squad")
            self.qa_model = AutoModelForQuestionAnswering.from_pretrained("distilbert-base-cased-distilled-squad")
            self.qa_pipeline = pipeline('question-answering', model=self.qa_model, tokenizer=self.tokenizer)
            
            logger.info("Transformer models loaded successfully")
        except Exception as e:
            logger.error(f"Transformer models loading error: {e}")
            self.sentiment_analyzer = None
            self.zero_shot_classifier = None
            self.qa_pipeline = None

        # File Paths with automatic directory creation
        self.base_dir = os.path.join(os.path.expanduser("~"), ".scydroid")
        os.makedirs(self.base_dir, exist_ok=True)
        
        self.paths = {
            'responses': os.path.join(self.base_dir, 'responses.txt'),
            'log': os.path.join(self.base_dir, 'interaction_logs.txt'),
            'knowledge_base': os.path.join(self.base_dir, 'advanced_knowledge_base.json'),
            'user_data': os.path.join(self.base_dir, 'user_profile.json'),
            'cache': os.path.join(self.base_dir, 'search_cache.json')
        }

        # Enhanced capabilities
        self.capabilities = {
            "1. Information Retrieval": [
                "Search the web for information",
                "Get quick definitions and explanations",
                "Explain complex topics in simple terms",
                "Answer questions using online resources when needed"
            ],
            "2. Task Management": [
                "Create and manage reminders",
                "Schedule appointments and events",
                "Set alarms and timers",
                "Organize and prioritize to-do lists"
            ],
            "3. Emotional Support": [
                "Mood analysis and tracking",
                "Provide personalized motivational quotes",
                "Offer empathetic responses based on sentiment",
                "Suggest stress management techniques"
            ],
            "4. Conversational Abilities": [
                "Natural free-flowing conversations",
                "Understand and respond to context",
                "Adapt to your conversational style",
                "Tell jokes and engage in small talk"
            ],
            "5. Advanced Features": [
                "Voice interaction with customizable settings",
                "Learn from your preferences over time",
                "Graceful handling of unexpected questions",
                "Integration with web searches for unknown topics"
            ]
        }

        # Expanded intent categories for better classification
        self.intent_categories = {
            'information_retrieval': [
                'what is', 'tell me about', 'define', 'explain', 
                'who is', 'when did', 'where is', 'how does', 'why is',
                'search for', 'look up', 'find information', 'research',
                'learn about', 'tell me more', 'details on', 'facts about'
            ],
            'task_management': [
                'remind me', 'schedule', 'plan', 'organize', 
                'create task', 'set alarm', 'calendar', 'appointment',
                'make a note', 'add to list', 'prioritize', 'deadline',
                'remember to', 'don\'t let me forget', 'task for'
            ],
            'emotional_support': [
                'feeling sad', 'help me', 'i am stressed', 
                'need advice', 'console me', 'cheer me up', 'feeling down',
                'anxious about', 'worried', 'depressed', 'overwhelmed',
                'lonely', 'frustrated', 'angry', 'emotional support'
            ],
            'conversational': [
                'how are you', 'what do you do', 'tell me a story', 
                'joke', 'chat', 'talk', 'let\'s discuss', 'your opinion',
                'what do you think', 'have you heard', 'did you know',
                'fun fact', 'interesting topic', 'small talk'
            ],
            'system_command': [
                'settings', 'configure', 'change', 'update', 'modify',
                'exit', 'quit', 'stop', 'shutdown', 'restart',
                'volume', 'speed', 'voice', 'help', 'instructions'
            ]
        }

        # Cache for web search results to improve response time
        self.search_cache = {}
        self.load_search_cache()
        
        # User profile for personalization
        self.user_profile = {'name': 'User', 'preferences': {}, 'conversation_history': []}
        self.load_user_profile()
        
        # Conversation context tracking
        self.conversation_context = {
            'last_topic': None,
            'questions_asked': [],
            'recent_responses': [],
            'sentiment_history': []
        }
        
        # Initialize core components
        self.ensure_files_exist()
        self.load_knowledge_base()
        self.train_intent_classifier()
        
        # Response variety enhancement
        self.response_styles = ['formal', 'casual', 'enthusiastic', 'empathetic', 'concise']
        self.current_style = 'casual'  # Default to a more conversational style

    def ensure_files_exist(self):
        """Ensure all necessary files exist with proper error handling."""
        for path in self.paths.values():
            try:
                if not os.path.exists(path):
                    with open(path, 'w') as f:
                        if path.endswith('.json'):
                            json.dump({}, f)
                            logger.info(f"Created new file: {path}")
            except Exception as e:
                logger.error(f"Error creating file {path}: {e}")
                # Create a backup location if default fails
                backup_path = os.path.join(os.getcwd(), os.path.basename(path))
                try:
                    with open(backup_path, 'w') as f:
                        if backup_path.endswith('.json'):
                            json.dump({}, f)
                    self.paths[path] = backup_path
                    logger.info(f"Created backup file at: {backup_path}")
                except Exception as e2:
                    logger.critical(f"Failed to create backup file: {e2}")

    def load_knowledge_base(self):
        """Load the knowledge base with robust error handling."""
        try:
            with open(self.paths['knowledge_base'], 'r') as f:
                self.knowledge_base = json.load(f)
            logger.info("Knowledge base loaded successfully")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Knowledge base loading error: {e}. Creating new knowledge base.")
            self.knowledge_base = {
                'responses': {},
                'user_preferences': {},
                'interaction_history': [],
                'facts': {}
            }
            self.save_knowledge_base()

    def save_knowledge_base(self):
        """Save the knowledge base with error handling."""
        try:
            with open(self.paths['knowledge_base'], 'w') as f:
                json.dump(self.knowledge_base, f, indent=4)
            logger.info("Knowledge base saved successfully")
        except Exception as e:
            logger.error(f"Error saving knowledge base: {e}")
            # Try backup location
            backup_path = os.path.join(os.getcwd(), 'kb_backup.json')
            try:
                with open(backup_path, 'w') as f:
                    json.dump(self.knowledge_base, f, indent=4)
                logger.info(f"Knowledge base saved to backup location: {backup_path}")
            except Exception as e2:
                logger.critical(f"Failed to save knowledge base to backup: {e2}")

    def load_search_cache(self):
        """Load the search cache for faster responses."""
        try:
            if os.path.exists(self.paths['cache']):
                with open(self.paths['cache'], 'r') as f:
                    self.search_cache = json.load(f)
                # Clean old cache entries (older than 1 week)
                current_time = datetime.datetime.now().timestamp()
                self.search_cache = {
                    k: v for k, v in self.search_cache.items() 
                    if current_time - v.get('timestamp', 0) < 604800  # 7 days in seconds
                }
        except Exception as e:
            logger.error(f"Error loading search cache: {e}")
            self.search_cache = {}

    def save_search_cache(self):
        """Save the search cache."""
        try:
            with open(self.paths['cache'], 'w') as f:
                json.dump(self.search_cache, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving search cache: {e}")

    def load_user_profile(self):
        """Load user profile for personalization."""
        try:
            if os.path.exists(self.paths['user_data']):
                with open(self.paths['user_data'], 'r') as f:
                    self.user_profile = json.load(f)
        except Exception as e:
            logger.error(f"Error loading user profile: {e}")
            # Create default profile
            self.user_profile = {'name': 'User', 'preferences': {}, 'conversation_history': []}

    def save_user_profile(self):
        """Save user profile with error handling."""
        try:
            with open(self.paths['user_data'], 'w') as f:
                json.dump(self.user_profile, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving user profile: {e}")

    def train_intent_classifier(self):
        """Train the intent classification model with error handling."""
        try:
            X_train = []
            y_train = []
            
            for intent, examples in self.intent_categories.items():
                X_train.extend(examples)
                y_train.extend([intent] * len(examples))
            
            self.vectorizer = TfidfVectorizer(stop_words='english')
            X_vectorized = self.vectorizer.fit_transform(X_train)
            
            self.label_encoder = LabelEncoder()
            y_encoded = self.label_encoder.fit_transform(y_train)
            
            self.intent_classifier = MLPClassifier(
                hidden_layer_sizes=(150, 75), 
                max_iter=1000, 
                activation='relu',
                solver='adam',
                alpha=0.0001,
                random_state=42
            )
            self.intent_classifier.fit(X_vectorized, y_encoded)
            logger.info("Intent classifier trained successfully")
        except Exception as e:
            logger.error(f"Error training intent classifier: {e}")
            # Fallback to rule-based intent classification
            self.intent_classifier = None
            logger.warning("Using fallback rule-based intent classification")

    def classify_intent(self, query):
        """Classify the intent with fallbacks if ML model fails."""
        try:
            if self.intent_classifier is not None:
                query_vectorized = self.vectorizer.transform([query])
                intent_encoded = self.intent_classifier.predict(query_vectorized)[0]
                return self.label_encoder.inverse_transform([intent_encoded])[0]
            else:
                return self.rule_based_intent_classification(query)
        except Exception as e:
            logger.error(f"Error classifying intent: {e}")
            return self.rule_based_intent_classification(query)

    def rule_based_intent_classification(self, query):
        """Fallback rule-based intent classification."""
        query = query.lower()
        
        # Simple keyword matching approach
        for intent, keywords in self.intent_categories.items():
            for keyword in keywords:
                if keyword in query:
                    return intent
        
        # Default to information retrieval for unknown queries
        return 'information_retrieval'

    def speak(self, text):
        """Text-to-speech method with error handling and interruption support."""
        print(f"ScyDroid: {text}")
        
        if self.engine is None:
            logger.warning("Text-to-speech engine not available")
            return
            
        try:
            # Stop any ongoing speech
            self.engine.stop()
        except:
            pass
            
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"Text-to-speech error: {e}")
            # Try reinitializing the engine
            try:
                self.engine = pyttsx3.init()
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e2:
                logger.critical(f"Failed to reinitialize speech engine: {e2}")

    def listen(self):
        """Enhanced speech recognition with background noise adjustment."""
        with sr.Microphone() as source:
            print("Listening...")
            try:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
                
                print("Processing speech...")
                
                # Try multiple recognition services for better accuracy
                text = None
                services = [
                    (self.recognizer.recognize_google, "Google"),
                    (self.recognizer.recognize_sphinx, "Sphinx")
                ]
                
                for recognizer_func, service_name in services:
                    try:
                        text = recognizer_func(audio)
                        logger.info(f"Speech recognized using {service_name}")
                        break
                    except Exception as e:
                        logger.warning(f"{service_name} recognition failed: {e}")
                        continue
                
                if text:
                    print(f"You said: {text}")
                    return text.lower()
                else:
                    self.speak("Sorry, I didn't catch that.")
                    return ""
                    
            except sr.WaitTimeoutError:
                self.speak("I didn't hear anything. Could you please speak again?")
                return ""
            except sr.UnknownValueError:
                self.speak("Sorry, I didn't understand that.")
                return ""
            except sr.RequestError as e:
                self.speak("Sorry, my speech service is having problems.")
                logger.error(f"Speech recognition service error: {e}")
                return ""
            except Exception as e:
                self.speak("There was an issue with the speech recognition.")
                logger.error(f"Unexpected speech recognition error: {e}")
                return ""

    def web_search(self, query):
        """Search the web for information when the query is not in knowledge base."""
        # Check cache first for faster response
        if query in self.search_cache:
            cache_entry = self.search_cache[query]
            # Check if cache is fresh (less than 1 day old)
            if time.time() - cache_entry.get('timestamp', 0) < 86400:  # 24 hours in seconds
                logger.info(f"Using cached search result for: {query}")
                return cache_entry['result']
        
        try:
            search_query = quote_plus(query)
            url = f"https://www.google.com/search?q={search_query}"
            
            # Set a user agent to avoid being blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract search result snippets
            snippets = []
            for div in soup.find_all('div', class_=['BNeawe s3v9rd AP7Wnd', 'BNeawe vvjwJb AP7Wnd']):
                snippet = div.get_text()
                if len(snippet) > 40:  # Ignore very short snippets
                    snippets.append(snippet)
            
            # Extract featured snippet if available
            featured_snippet = ""
            featured_div = soup.find('div', class_='xpdopen')
            if featured_div:
                featured_text = featured_div.find('div', class_='BNeawe s3v9rd AP7Wnd')
                if featured_text:
                    featured_snippet = featured_text.get_text()
            
            # Combine and format results
            if featured_snippet:
                result = f"Here's what I found: {featured_snippet}"
            elif snippets:
                result = f"Based on my search: {' '.join(snippets[:2])}"
            else:
                result = "I couldn't find specific information about that, but I'll keep learning."
            
            # Cache the result
            self.search_cache[query] = {
                'result': result,
                'timestamp': time.time()
            }
            self.save_search_cache()
            
            return result
            
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return "I tried to search for information, but encountered an issue. Can you try asking in a different way?"

    def answer_with_qa_model(self, query, context):
        """Use question-answering model for better responses."""
        if not self.qa_pipeline:
            return None
            
        try:
            result = self.qa_pipeline(question=query, context=context)
            if result['score'] > 0.3:  # Confidence threshold
                return result['answer']
        except Exception as e:
            logger.error(f"QA model error: {e}")
        
        return None

    def display_capabilities(self):
        """Display AI capabilities with improved formatting."""
        print("\n" + "=" * 60)
        print("🤖 ScyDroid AI - Capabilities & Features 🤖")
        print("=" * 60)
        
        for category, features in self.capabilities.items():
            print(f"\n{category}")
            print("-" * len(category))
            for feature in features:
                print(f"• {feature}")
        
        print("\n" + "-" * 60)
        print("To interact with ScyDroid, simply type your question or request.")
        print("You can ask for information, request tasks, or just chat!")
        print("-" * 60)
        
        input("\nPress Enter to continue...")

    def main_menu(self):
        """Enhanced main interaction menu."""
        while True:
            try:
                print("\n" + "=" * 60)
                print("🤖 ScyDroid AI - Main Menu 🤖")
                print("=" * 60)
                print("1. Chat with ScyDroid")
                print("2. Voice Interaction")
                print("3. View Capabilities")
                print("4. Settings")
                print("5. Exit")
                
                choice = input("Enter your choice (1-5): ")
                
                if choice == '1':
                    self.interactive_mode(voice_mode=False)
                elif choice == '2':
                    self.interactive_mode(voice_mode=True)
                elif choice == '3':
                    self.display_capabilities()
                elif choice == '4':
                    self.settings_menu()
                elif choice == '5':
                    self.speak("Goodbye! Have a great day!")
                    break
                else:
                    print("Invalid choice. Please enter a number between 1 and 5.")
            except KeyboardInterrupt:
                print("\nOperation interrupted. Returning to main menu...")
            except Exception as e:
                logger.error(f"Main menu error: {e}")
                print(f"An error occurred. Please try again.")

    def interactive_mode(self, voice_mode=False):
        """Interactive conversation mode with enhanced responsiveness."""
        welcome_messages = [
            "Hello! I'm ScyDroid. How can I help you today?",
            "Hi there! I'm ready to assist you. What can I do for you?",
            f"Hello{' ' + self.user_profile['name'] if self.user_profile['name'] != 'User' else ''}! What would you like to talk about?",
            "Greetings! I'm ScyDroid, your AI assistant. How may I help you?"
        ]
        
        self.speak(random.choice(welcome_messages))
        
        while True:
            try:
                # Get user input
                if voice_mode:
                    query = self.listen()
                    if not query:
                        continue
                else:
                    query = input("You: ")
                
                # Check for exit commands
                if query.lower() in ['exit', 'bye', 'goodbye', 'quit', 'leave']:
                    farewell_messages = [
                        "Goodbye! It was nice chatting with you.",
                        "See you later! Have a great day!",
                        "Bye for now! Feel free to chat again anytime.",
                        "Farewell! I'll be here when you need me."
                    ]
                    self.speak(random.choice(farewell_messages))
                    break
                
                # Show typing indicator for better user experience
                print("ScyDroid is thinking...", end="\r")
                
                # Set processing flag to avoid interruption
                self.is_processing = True
                
                # Process the query in background for responsiveness
                future = self.thread_pool.submit(self.process_query, query)
                
                # Wait for processing with timeout
                try:
                    response = future.result(timeout=10)
                except Exception as e:
                    logger.error(f"Query processing timed out: {e}")
                    response = "I'm sorry, but I'm having trouble processing that request. Could you try again or phrase it differently?"
                
                # Clear thinking indicator
                print(" " * 30, end="\r")
                
                # Speak the response
                self.speak(response)
                
                # Update conversation context
                self.update_conversation_context(query, response)
                
                # Log interaction
                self.log_interaction(query, response)
                
                # Reset processing flag
                self.is_processing = False
                
            except KeyboardInterrupt:
                print("\nInteraction interrupted. Returning to main menu...")
                break
            except Exception as e:
                logger.error(f"Interactive mode error: {e}")
                self.speak("I encountered an unexpected issue. Let's continue our conversation.")
                self.is_processing = False

    def process_query(self, query):
        """Process user query with comprehensive error handling and fallbacks."""
        try:
            # Classify intent
            intent = self.classify_intent(query)
            logger.info(f"Classified intent: {intent} for query: {query}")
            
            # Check for follow-up questions using conversation context
            is_followup = self.check_if_followup(query)
            
            # Analyze sentiment if available
            sentiment = "neutral"
            if self.sentiment_analyzer:
                try:
                    sentiment_result = self.sentiment_analyzer(query)
                    sentiment = sentiment_result[0]['label']
                    self.conversation_context['sentiment_history'].append(sentiment)
                except Exception as e:
                    logger.error(f"Sentiment analysis error: {e}")
            
            # Generate response based on intent and conversation context
            response = self.generate_enhanced_response(query, intent, is_followup, sentiment)
            
            return response
            
        except Exception as e:
            logger.error(f"Query processing error: {e}")
            return "I'm having trouble understanding that. Could you rephrase your question?"

    def check_if_followup(self, query):
        """Check if current query is a follow-up to previous conversation."""
        if not self.conversation_context['last_topic']:
            return False
            
        # Look for pronouns that might indicate follow-up
        followup_indicators = ['it', 'that', 'this', 'they', 'them', 'those', 'these']
        query_words = query.lower().split()
        
        # Check if query starts with followup indicators
        if any(query.lower().startswith(word) for word in followup_indicators):
            return True
            
        # Check for very short queries which are often follow-ups
        if len(query_words) <= 3 and not any(q in query.lower() for q in ['who', 'what', 'where', 'when', 'why', 'how']):
            return True
            
        return False

    def generate_enhanced_response(self, query, intent, is_followup, sentiment):
        """Generate contextual response with web search fallback."""
        # First try knowledge base
        known_response = self.check_knowledge_base(query)
        if known_response:
            return known_response
            
        # If follow-up, use conversation context
        if is_followup and self.conversation_context['last_topic']:
            context_query = f"{self.conversation_context['last_topic']} {query}"
            # Try QA model with context first
            if self.qa_pipeline and self.conversation_context['recent_responses']:
                context = ' '.join(self.conversation_context['recent_responses'][-3:])
                qa_response = self.answer_with_qa_model(query, context)
                if qa_response:
                    return qa_response
                    
            # Fallback to web search with context
            return self.web_search(context_query)
            
        # Handle by intent
        if intent == 'information_retrieval':
            # Try QA model first if available
            if self.qa_pipeline and self.knowledge_base.get('facts'):
                # Create context from relevant facts
                relevant_facts = []
                for topic, fact in self.knowledge_base['facts'].items():
                    if any(word in query.lower() for word in topic.lower().split()):
                        relevant_facts.append(fact)
                
                if relevant_facts:
                    context = ' '.join(relevant_facts)
                    qa_response = self.answer_with_qa_model(query, context)
                    if qa_response:
                        return qa_response
            
            # Fallback to web search
            search_result = self.web_search(query)
            
            # Save this fact for future reference
            if len(query.split()) >= 3 and len(search_result.split()) >= 10:
                topic = ' '.join(query.split()[:3])
                self.knowledge_base['facts'][topic] = search_result
                self.save_knowledge_base()
                
            return search_result
            
        elif intent == 'emotional_support':
            # Tailor response based on sentiment
            if sentiment == 'NEGATIVE':
                responses = [
                    "I'm sorry to hear you're feeling that way. Would you like to talk about it?",
                    "That sounds difficult. Remember that it's okay to have these feelings.",
                    "I'm here for you. Sometimes talking about things can help.",
                    "I understand this is challenging. What might help you feel better right now?"
                ]
            else:
                responses = [
                    "I'm here to support you. How can I help?",
                    "Let's work through this together. What's on your mind?",
                    "I'm listening. Sometimes sharing can make things clearer.",
                    "I'm glad you're reaching out. How can I best assist you?"
                ]
            return random.choice(responses)
            
        elif intent == 'task_management':
            tasks = ["reminder", "schedule", "appointment", "task", "to-do", "list"]
            task_type = next((t for t in tasks if t in query.lower()), "task")
            
            responses = [
                f"I can help you with that {task_type}. What details should I include?",
                f"I'll assist you in managing this {task_type}. What are the key points?",
                f"Let's set up that {task_type}. What time and date would you prefer?",
                f"I can organize this {task_type} for you. Any specific requirements?"
            ]
            return random.choice(responses)
            
        elif intent == 'conversational':
            # More natural conversational responses
            greetings = ["hi", "hello", "hey", "greetings"]
            if any(greeting in query.lower() for greeting in greetings):
                return random.choice([
                    f"Hello! How are you doing today?",
                    f"Hi there! What's on your mind?",
                    f"Hey! It's great to chat with you. How can I help?",
                    f"Greetings! How's your day going?"
                ])
                
            how_are_you = ["how are you", "how're you", "how you doing", "how's it going"]
            if any(phrase in query.lower() for phrase in how_are_you):
                return random.choice([
                    "I'm doing well, thanks for asking! How about you?",
                    "I'm great! Always happy to assist. What can I help you with today?",
                    "I'm functioning optimally! But more importantly, how are you doing?",
                    "All systems running smoothly on my end. How's your day going?"
                ])
            
            # Joke handling
            if "joke" in query.lower() or "funny" in query.lower():
                jokes = [
                    "Why don't scientists trust atoms? Because they make up everything!",
                    "What did the AI say to the cup of coffee? 'You're my daily java!'",
                    "Why did the computer go to art school? It wanted to learn how to draw pixels!",
                    "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
                    "I asked my AI assistant to tell me a joke about artificial intelligence... it's still computing."
                ]
                return random.choice(jokes)
                
            # For other conversational queries, give a thoughtful response
            return random.choice([
                "That's an interesting topic. What aspects would you like to explore?",
                "I enjoy conversations like this. Do you have any specific thoughts about it?",
                "I'm happy to chat about that. What's your perspective?",
                "That's something I can discuss. Would you like to know anything specific?"
            ])
            
        elif intent == 'system_command':
            if any(word in query.lower() for word in ['settings', 'configure', 'setup']):
                return "I can help you with settings. You can adjust voice, language, or reset my knowledge base through the settings menu."
            elif any(word in query.lower() for word in ['help', 'instructions', 'guide']):
                return "I'm here to help! You can ask me questions, request tasks, chat, or get emotional support. What would you like to know about?"
                
        # Default response for unknown intents
        return self.web_search(query)

    def check_knowledge_base(self, query):
        """Check if query matches anything in knowledge base."""
        # Clean query for matching
        clean_query = re.sub(r'[^\w\s]', '', query.lower())
        words = clean_query.split()
        
        # Check for exact matches
        if clean_query in self.knowledge_base['responses']:
            return self.knowledge_base['responses'][clean_query]
            
        # Check for partial matches
        for key, value in self.knowledge_base['responses'].items():
            key_words = set(key.split())
            query_words = set(words)
            # If 70% of words match
            if len(key_words.intersection(query_words)) / max(len(key_words), len(query_words)) >= 0.7:
                return value
                
        return None

    def update_conversation_context(self, query, response):
        """Update conversation context for better follow-up handling."""
        # Extract potential topic
        topic_words = [word for word in query.lower().split() 
                    if word not in ['what', 'who', 'where', 'when', 'why', 'how', 
                                    'is', 'are', 'was', 'were', 'do', 'does', 'did',
                                    'a', 'an', 'the', 'to', 'in', 'on', 'of']]
        
        if topic_words:
            self.conversation_context['last_topic'] = ' '.join(topic_words[:3])
            
        # Update question history
        self.conversation_context['questions_asked'].append(query)
        if len(self.conversation_context['questions_asked']) > 10:
            self.conversation_context['questions_asked'] = self.conversation_context['questions_asked'][-10:]
            
        # Update response history
        self.conversation_context['recent_responses'].append(response)
        if len(self.conversation_context['recent_responses']) > 5:
            self.conversation_context['recent_responses'] = self.conversation_context['recent_responses'][-5:]
            
        # Update user profile
        self.user_profile['conversation_history'].append({
            'query': query,
            'response': response,
            'timestamp': datetime.datetime.now().isoformat()
        })
        
        # Keep conversation history manageable
        if len(self.user_profile['conversation_history']) > 50:
            self.user_profile['conversation_history'] = self.user_profile['conversation_history'][-50:]
            
        # Save updated user profile
        self.save_user_profile()

    def log_interaction(self, query, response):
        """Log user interactions with timestamp."""
        try:
            with open(self.paths['log'], 'a') as f:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{timestamp} - User: {query}\n")
                f.write(f"{timestamp} - ScyDroid: {response}\n\n")
        except Exception as e:
            logger.error(f"Error logging interaction: {e}")

    def settings_menu(self):
        """Enhanced settings and configuration menu."""
        while True:
            print("\n" + "=" * 60)
            print("ScyDroid AI - Settings")
            print("=" * 60)
            print("1. Voice Settings")
            print("2. Personalization")
            print("3. Chat Style Preferences")
            print("4. Reset Knowledge Base")
            print("5. System Information")
            print("6. Back to Main Menu")
            
            try:
                choice = input("Enter your choice (1-6): ")
                
                if choice == '1':
                    self.voice_settings()
                elif choice == '2':
                    self.personalization_settings()
                elif choice == '3':
                    self.chat_style_settings()
                elif choice == '4':
                    self.reset_knowledge_base()
                elif choice == '5':
                    self.system_information()
                elif choice == '6':
                    break
                else:
                    print("Invalid choice. Please enter a number between 1 and 6.")
            except Exception as e:
                logger.error(f"Settings menu error: {e}")
                print("An error occurred. Returning to settings menu.")

    def voice_settings(self):
        """Enhanced voice settings with previews."""
        while True:
            print("\n" + "=" * 60)
            print("Voice Settings")
            print("=" * 60)
            
            if self.engine is None:
                print("Text-to-speech is currently unavailable.")
                input("Press Enter to return to settings...")
                return
                
            current_rate = self.engine.getProperty('rate')
            current_volume = self.engine.getProperty('volume')
            current_voice_id = self.engine.getProperty('voice')
            
            print(f"1. Change Voice (Current: Voice #{self.voice_options.index(next((v for v in self.voice_options if v.id == current_voice_id), self.voice_options[0]))+1})")
            print(f"2. Adjust Speed (Current: {current_rate})")
            print(f"3. Adjust Volume (Current: {current_volume*100}%)")
            print("4. Preview Current Voice")
            print("5. Back to Settings")
            
            choice = input("Enter your choice (1-5): ")
            
            try:
                if choice == '1':
                    print("\nAvailable Voices:")
                    for i, voice in enumerate(self.voice_options):
                        gender = "Male" if "male" in voice.name.lower() else "Female"
                        print(f"{i+1}. {voice.name} ({gender})")
                    
                    voice_choice = input(f"Select voice (1-{len(self.voice_options)}): ")
                    voice_index = int(voice_choice) - 1
                    
                    if 0 <= voice_index < len(self.voice_options):
                        self.engine.setProperty('voice', self.voice_options[voice_index].id)
                        print(f"Voice changed to {self.voice_options[voice_index].name}")
                        self.speak("This is how I sound now. Is this voice better?")
                    else:
                        print("Invalid selection.")
                        
                elif choice == '2':
                    print("Speed options:")
                    print("1. Slow (125)")
                    print("2. Normal (175)")
                    print("3. Fast (225)")
                    print("4. Very Fast (275)")
                    print("5. Custom")
                    
                    speed_choice = input("Select speed (1-5): ")
                    
                    if speed_choice == '1':
                        self.engine.setProperty('rate', 125)
                    elif speed_choice == '2':
                        self.engine.setProperty('rate', 175)
                    elif speed_choice == '3':
                        self.engine.setProperty('rate', 225)
                    elif speed_choice == '4':
                        self.engine.setProperty('rate', 275)
                    elif speed_choice == '5':
                        custom_speed = input("Enter custom speed (100-300): ")
                        try:
                            speed = int(custom_speed)
                            if 100 <= speed <= 300:
                                self.engine.setProperty('rate', speed)
                            else:
                                print("Speed must be between 100 and 300.")
                        except ValueError:
                            print("Please enter a valid number.")
                    
                    self.speak("This is how fast I'm speaking now. Is this speed comfortable?")
                    
                elif choice == '3':
                    print("Volume options:")
                    print("1. Quiet (50%)")
                    print("2. Normal (75%)")
                    print("3. Loud (100%)")
                    print("4. Custom")
                    
                    volume_choice = input("Select volume (1-4): ")
                    
                    if volume_choice == '1':
                        self.engine.setProperty('volume', 0.5)
                    elif volume_choice == '2':
                        self.engine.setProperty('volume', 0.75)
                    elif volume_choice == '3':
                        self.engine.setProperty('volume', 1.0)
                    elif volume_choice == '4':
                        custom_volume = input("Enter custom volume (10-100%): ")
                        try:
                            volume = int(custom_volume)
                            if 10 <= volume <= 100:
                                self.engine.setProperty('volume', volume/100)
                            else:
                                print("Volume must be between 10 and 100.")
                        except ValueError:
                            print("Please enter a valid number.")
                    
                    self.speak("This is my current volume level. Is this acceptable?")
                    
                elif choice == '4':
                    self.speak("This is a preview of my current voice settings. How do I sound?")
                    
                elif choice == '5':
                    break
                else:
                    print("Invalid choice. Please try again.")
            except Exception as e:
                logger.error(f"Voice settings error: {e}")
                print("An error occurred while adjusting voice settings.")

    def personalization_settings(self):
        """Personalization settings for customized experience."""
        print("\n" + "=" * 60)
        print("Personalization Settings")
        print("=" * 60)
        
        print(f"Current Name: {self.user_profile['name']}")
        
        name_choice = input("Would you like me to call you by a different name? (y/n): ")
        if name_choice.lower() == 'y':
            new_name = input("Enter your preferred name: ")
            self.user_profile['name'] = new_name
            self.save_user_profile()
            print(f"I'll call you {new_name} from now on.")
        
        print("\nPreferences:")
        print("1. Set preferred response length (brief/detailed)")
        print("2. Toggle technical explanations (simple/technical)")
        print("3. Back to settings")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            print("\nResponse Length Preference:")
            print("1. Brief (Concise answers)")
            print("2. Standard (Balanced detail)")
            print("3. Detailed (Comprehensive responses)")
            
            length_choice = input("Select preference (1-3): ")
            
            if length_choice in ['1', '2', '3']:
                length_map = {'1': 'brief', '2': 'standard', '3': 'detailed'}
                self.user_profile['preferences']['response_length'] = length_map[length_choice]
                self.save_user_profile()
                print(f"Response length preference set to {length_map[length_choice]}.")
                
        elif choice == '2':
            print("\nExplanation Style Preference:")
            print("1. Simple (Non-technical language)")
            print("2. Balanced (Moderate technical terms)")
            print("3. Technical (Detailed technical explanations)")
            
            tech_choice = input("Select preference (1-3): ")
            
            if tech_choice in ['1', '2', '3']:
                tech_map = {'1': 'simple', '2': 'balanced', '3': 'technical'}
                self.user_profile['preferences']['technical_level'] = tech_map[tech_choice]
                self.save_user_profile()
                print(f"Technical explanation preference set to {tech_map[tech_choice]}.")

    def chat_style_settings(self):
        """Settings for chat interaction style."""
        print("\n" + "=" * 60)
        print("Chat Style Preferences")
        print("=" * 60)
        print("Choose your preferred chat style:")
        print("1. Formal (Professional and precise)")
        print("2. Casual (Friendly and conversational)")
        print("3. Enthusiastic (Upbeat and energetic)")
        print("4. Empathetic (Supportive and understanding)")
        print("5. Concise (Brief and to-the-point)")
        
        style_choice = input("Select style (1-5): ")
        
        style_map = {
            '1': 'formal', 
            '2': 'casual', 
            '3': 'enthusiastic',
            '4': 'empathetic',
            '5': 'concise'
        }
        
        if style_choice in style_map:
            self.current_style = style_map[style_choice]
            self.user_profile['preferences']['chat_style'] = self.current_style
            self.save_user_profile()
            
            style_examples = {
                'formal': "I've updated your chat style preference to formal. I'll maintain a professional tone in our interactions.",
                'casual': "Cool! I've switched to a more casual style. Let's chat in a more relaxed way now!",
                'enthusiastic': "Awesome choice! I'm super excited about using this enthusiastic style with you! Let's make our conversations fun and energetic!",
                'empathetic': "I understand you prefer a more supportive style. I'm here for you, and I'll focus on being understanding and empathetic in our conversations.",
                'concise': "Style updated to concise. I'll keep responses brief."
            }
            
            self.speak(style_examples[self.current_style])

    def reset_knowledge_base(self):
        """Reset the knowledge base with confirmation."""
        print("\n" + "=" * 60)
        print("Reset Knowledge Base")
        print("=" * 60)
        print("WARNING: This will erase all learned responses and preferences.")
        print("Your conversation history will remain intact.")
        
        confirm = input("Are you sure you want to reset? (type 'RESET' to confirm): ")
        if confirm.upper() == 'RESET':
            try:
                self.knowledge_base = {
                    'responses': {},
                    'user_preferences': {},
                    'interaction_history': [],
                    'facts': {}
                }
                self.save_knowledge_base()
                
                # Clear search cache too
                self.search_cache = {}
                self.save_search_cache()
                
                self.speak("Knowledge base has been reset successfully.")
            except Exception as e:
                logger.error(f"Error resetting knowledge base: {e}")
                self.speak("There was an error resetting the knowledge base.")
        else:
            print("Reset cancelled.")

    def system_information(self):
        """Display system information and diagnostics."""
        print("\n" + "=" * 60)
        print("System Information")
        print("=" * 60)
        
        # Collect system status
        status = {
            "Version": "2.0.0",
            "Text-to-Speech": "Available" if self.engine is not None else "Unavailable",
            "Speech Recognition": "Available",
            "NLP Processing": "Available" if self.nlp is not None else "Limited",
            "ML Capabilities": "Available" if self.intent_classifier is not None else "Limited",
            "Transformer Models": "Available" if self.sentiment_analyzer is not None else "Unavailable",
            "Web Search": "Enabled",
            "Knowledge Base": f"{len(self.knowledge_base.get('responses', {}))} stored responses",
            "Facts Database": f"{len(self.knowledge_base.get('facts', {}))} stored facts",
            "Search Cache": f"{len(self.search_cache)} cached searches"
        }
        
        # Display status
        for key, value in status.items():
            print(f"{key}: {value}")
        
        print("\nStorage Locations:")
        for name, path in self.paths.items():
            exists = "✓" if os.path.exists(path) else "✗"
            print(f"{name}: {path} {exists}")
        
        # Run diagnostics
        print("\nRunning quick diagnostics...")
        
        try:
            # Test TTS
            if self.engine is not None:
                print("Text-to-Speech: OK")
            else:
                print("Text-to-Speech: UNAVAILABLE")
            
            # Test intent classification
            if self.intent_classifier is not None:
                test_query = "what is the weather today"
                intent = self.classify_intent(test_query)
                print(f"Intent Classification: OK ('{test_query}' → '{intent}')")
            else:
                print("Intent Classification: LIMITED (using rule-based fallback)")
            
            # Test web connectivity
            try:
                requests.get("https://www.google.com", timeout=3)
                print("Internet Connectivity: OK")
            except:
                print("Internet Connectivity: UNAVAILABLE")
                
        except Exception as e:
            logger.error(f"Diagnostics error: {e}")
            print(f"Diagnostics error: {str(e)}")
            
        input("\nPress Enter to return to settings...")

    def run(self):
        """Main run method with enhanced error handling."""
        try:
            welcome_message = "ScyDroid AI Initialized. Welcome to version 2.0!"
            print("\n" + "=" * 60)
            print(welcome_message)
            print("=" * 60)
            
            self.speak(welcome_message)
            self.main_menu()
            
        except KeyboardInterrupt:
            print("\nScyDroid AI shutting down...")
            self.speak("Goodbye!")
        except Exception as e:
            logger.critical(f"Critical error in main run: {e}")
            print(f"A critical error occurred: {str(e)}")
            print("ScyDroid AI will attempt to restart...")
            
            try:
                # Save any unsaved data
                self.save_knowledge_base()
                self.save_user_profile()
                self.save_search_cache()
                
                # Restart main menu
                self.speak("I encountered an issue. Let me restart.")
                self.main_menu()
            except:
                print("Unable to recover. Please restart ScyDroid AI manually.")
        finally:
            # Clean shutdown
            if self.thread_pool:
                self.thread_pool.shutdown(wait=False)

def main():
    """Main entry point with error handling."""
    try:
        print("Starting ScyDroid AI...")
        ai = AdvancedScyDroidAI()
        ai.run()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        logging.critical(f"Fatal error in main: {e}")
        print("ScyDroid AI has encountered a critical error and needs to close.")
        print("Check the log file for details.")

if __name__ == "__main__":
    main()
