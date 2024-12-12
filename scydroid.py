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

from nltk.corpus import wordnet
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder
from transformers import pipeline

# Ensure NLTK resources are downloaded
nltk.download('wordnet', quiet=True)
nltk.download('punkt', quiet=True)

class AdvancedScyDroidAI:
    def __init__(self):
        # Speech and Text Initialization
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()

        # NLP Setup
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except:
            print("SpaCy model not found. Some advanced NLP features will be limited.")
            self.nlp = None

        # Transformer Models
        try:
            self.sentiment_analyzer = pipeline('sentiment-analysis')
            self.zero_shot_classifier = pipeline('zero-shot-classification')
        except:
            print("Transformer models not fully loaded. Some advanced features may be limited.")
            self.sentiment_analyzer = None
            self.zero_shot_classifier = None

        # File Paths
        self.paths = {
            'responses': 'responses.txt',
            'log': 'interaction_logs.txt',
            'knowledge_base': 'advanced_knowledge_base.json',
            'user_data': 'user_profile.json'
        }

        # Capabilities and Intents
        self.capabilities = {
            "1. Information Retrieval": [
                "Search Wikipedia",
                "Get quick definitions",
                "Explain complex topics",
                "Provide background information"
            ],
            "2. Task Management": [
                "Create reminders",
                "Schedule appointments",
                "Set alarms",
                "Manage to-do lists"
            ],
            "3. Emotional Support": [
                "Mood analysis",
                "Provide motivational quotes",
                "Offer listening and empathy",
                "Stress management suggestions"
            ],
            "4. Conversational Abilities": [
                "Tell jokes",
                "Engage in small talk",
                "Answer questions about myself",
                "Provide witty responses"
            ]
        }

        # Intent Categories
        self.intent_categories = {
            'information_retrieval': [
                'what is', 'tell me about', 'define', 'explain', 
                'who is', 'when did', 'where is', 'how does'
            ],
            'task_management': [
                'remind me', 'schedule', 'plan', 'organize', 
                'create task', 'set alarm', 'calendar'
            ],
            'emotional_support': [
                'feeling sad', 'help me', 'i am stressed', 
                'need advice', 'console me', 'cheer me up'
            ],
            'conversational': [
                'how are you', 'what do you do', 'tell me a story', 
                'joke', 'chat', 'talk'
            ]
        }

        # Initialize core components
        self.ensure_files_exist()
        self.load_knowledge_base()
        self.train_intent_classifier()

    def ensure_files_exist(self):
        """Ensure all necessary files exist."""
        for path in self.paths.values():
            if not os.path.exists(path):
                with open(path, 'w') as f:
                    if path.endswith('.json'):
                        json.dump({}, f)

    def load_knowledge_base(self):
        """Load the knowledge base from file."""
        try:
            with open(self.paths['knowledge_base'], 'r') as f:
                self.knowledge_base = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.knowledge_base = {
                'responses': {},
                'user_preferences': {},
                'interaction_history': []
            }

    def save_knowledge_base(self):
        """Save the knowledge base to file."""
        with open(self.paths['knowledge_base'], 'w') as f:
            json.dump(self.knowledge_base, f, indent=4)

    def train_intent_classifier(self):
        """Train the intent classification model."""
        X_train = []
        y_train = []
        
        for intent, examples in self.intent_categories.items():
            X_train.extend(examples)
            y_train.extend([intent] * len(examples))
        
        vectorizer = TfidfVectorizer(stop_words='english')
        X_vectorized = vectorizer.fit_transform(X_train)
        
        label_encoder = LabelEncoder()
        y_encoded = label_encoder.fit_transform(y_train)
        
        self.intent_classifier = MLPClassifier(
            hidden_layer_sizes=(100, 50), 
            max_iter=500, 
            random_state=42
        )
        self.intent_classifier.fit(X_vectorized, y_encoded)
        
        self.vectorizer = vectorizer
        self.label_encoder = label_encoder

    def classify_intent(self, query):
        """Classify the intent of a given query."""
        query_vectorized = self.vectorizer.transform([query])
        intent_encoded = self.intent_classifier.predict(query_vectorized)[0]
        return self.label_encoder.inverse_transform([intent_encoded])[0]

    def speak(self, text):
        """Text-to-speech method."""
        print(f"ScyDroid: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        """Speech recognition method."""
        with sr.Microphone() as source:
            print("Listening...")
            audio = self.recognizer.listen(source)
            try:
                text = self.recognizer.recognize_google(audio)
                print(f"You said: {text}")
                return text.lower()
            except sr.UnknownValueError:
                self.speak("Sorry, I didn't catch that.")
                return ""
            except sr.RequestError:
                self.speak("Sorry, my speech service is down.")
                return ""

    def display_capabilities(self):
        """Display AI capabilities."""
        print("\n" + "=" * 50)
        print("🤖 ScyDroid AI - Capabilities 🤖")
        print("=" * 50)
        
        for category, features in self.capabilities.items():
            print(f"\n{category}")
            print("-" * len(category))
            for feature in features:
                print(f"• {feature}")
        
        input("\nPress Enter to continue...")

    def main_menu(self):
        """Main interaction menu."""
        while True:
            print("\n" + "=" * 50)
            print("ScyDroid AI - Main Menu")
            print("=" * 50)
            print("1. Chat with AI")
            print("2. View Capabilities")
            print("3. Settings")
            print("4. Exit")
            
            choice = input("Enter your choice: ")
            
            if choice == '1':
                self.interactive_mode()
            elif choice == '2':
                self.display_capabilities()
            elif choice == '3':
                self.settings_menu()
            elif choice == '4':
                self.speak("Goodbye! Have a great day!")
                break
            else:
                print("Invalid choice. Please try again.")

    def interactive_mode(self):
        """Interactive conversation mode."""
        self.speak("Hello! I'm ScyDroid. How can I help you today?")
        
        while True:
            query = input("You: ").lower()
            
            if query in ['exit', 'bye', 'goodbye']:
                self.speak("Goodbye! It was nice chatting with you.")
                break
            
            # Classify intent
            intent = self.classify_intent(query)
            
            # Generate response based on intent
            response = self.generate_response(query, intent)
            
            # Speak the response
            self.speak(response)
            
            # Log interaction
            self.log_interaction(query, response)

    def generate_response(self, query, intent):
        """Generate contextual response based on intent."""
        response_templates = {
            'information_retrieval': [
                "Let me help you find information about {}.",
                "Here's what I know about {}.",
                "Interesting query! Let me search for details."
            ],
            'task_management': [
                "I can help you manage that task.",
                "Let's organize this for you.",
                "I'll assist you in planning this."
            ],
            'emotional_support': [
                "I'm here to support you.",
                "Your feelings are valid.",
                "Let's work through this together."
            ],
            'conversational': [
                "That's an interesting topic!",
                "I'd be happy to chat about that.",
                "Tell me more!"
            ]
        }
        
        # Select appropriate template
        templates = response_templates.get(intent, ["I'm not quite sure how to respond."])
        response = random.choice(templates)
        
        return response.format(query)

    def log_interaction(self, query, response):
        """Log user interactions."""
        with open(self.paths['log'], 'a') as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} - User: {query}\n")
            f.write(f"{timestamp} - ScyDroid: {response}\n")

    def settings_menu(self):
        """Settings and configuration menu."""
        while True:
            print("\n" + "=" * 50)
            print("ScyDroid AI - Settings")
            print("=" * 50)
            print("1. Voice Settings")
            print("2. Language Preferences")
            print("3. Reset Knowledge Base")
            print("4. Back to Main Menu")
            
            choice = input("Enter your choice: ")
            
            if choice == '1':
                self.voice_settings()
            elif choice == '2':
                self.language_preferences()
            elif choice == '3':
                self.reset_knowledge_base()
            elif choice == '4':
                break
            else:
                print("Invalid choice. Please try again.")

    def voice_settings(self):
        """Adjust voice settings."""
        print("Voice Settings:")
        print("1. Change Voice")
        print("2. Adjust Speed")
        print("3. Adjust Volume")

    def language_preferences(self):
        """Set language preferences."""
        print("Language Preferences:")
        print("Currently supported: English")
        input("Press Enter to continue...")

    def reset_knowledge_base(self):
        """Reset the knowledge base."""
        confirm = input("Are you sure you want to reset the knowledge base? (yes/no): ")
        if confirm.lower() == 'yes':
            self.knowledge_base = {
                'responses': {},
                'user_preferences': {},
                'interaction_history': []
            }
            self.save_knowledge_base()
            self.speak("Knowledge base has been reset.")

    def run(self):
        """Main run method to start the AI."""
        self.speak("ScyDroid AI Initialized. Welcome!")
        self.main_menu()

def main():
    ai = AdvancedScyDroidAI()
    ai.run()

if __name__ == "__main__":
    main()
