import os
import pickle
import random
import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser
import wikipedia
from fuzzywuzzy import fuzz  # For fuzzy string matching
import re  # For URL validation
import time
from threading import Timer
import spacy  # For input analysis

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Initialize memory and preferences
stored_responses = {}
response_file_path = "responses.txt"
user_preferences = {"jokes": 0, "quotes": 0, "wikipedia": 0}
session_memory = {}
log_file_path = "interaction_logs.txt"

# Load spaCy model for input analysis
nlp = spacy.load("en_core_web_sm")

def talk(text):
    print(text)
    engine.say(text)
    engine.runAndWait()

def load_responses():
    if os.path.exists(response_file_path):
        with open(response_file_path, "r") as file:
            for line in file:
                if "::" in line:
                    query, response = line.strip().split("::", 1)
                    stored_responses[query.lower()] = response

def save_responses():
    with open(response_file_path, "w") as file:
        for query, response in stored_responses.items():
            file.write(f"{query}::{response}\n")

def log_interaction(query, response):
    # Log the interaction with timestamp
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{datetime.datetime.now()} - User: {query} - Assistant: {response}\n")

def analyze_logs():
    # Read and analyze the log file to generate context-based responses
    if not os.path.exists(log_file_path):
        return "I haven't had enough conversations to understand you yet."

    with open(log_file_path, "r") as log_file:
        logs = log_file.readlines()
    
    # Example: Analyzing frequency of queries and responses
    query_frequency = {}
    for log in logs:
        query = log.split("-")[1].split(":")[1].strip()
        if query in query_frequency:
            query_frequency[query] += 1
        else:
            query_frequency[query] = 1
    
    # Generate response based on frequent queries or patterns
    most_frequent_query = max(query_frequency, key=query_frequency.get)
    return f"You often ask about {most_frequent_query}. Maybe I can help you more with that?"

def learn_from_input(input_text):
    talk(f"Oops, I don't know how to respond to: '{input_text}'")
    talk("Can you help me out? What should I say when someone asks about that?")
    new_response = take_command(input_method)
    stored_responses[input_text] = new_response
    save_responses()
    talk(f"Yay, thanks! I’ll remember that for next time.")

def casual_greeting():
    current_hour = datetime.datetime.now().hour
    if 5 <= current_hour < 12:
        talk("Good morning! How’s it going today?")
    elif 12 <= current_hour < 17:
        talk("Hey there, good afternoon! What’s new?")
    elif 17 <= current_hour < 22:
        talk("Good evening! How’s your day been?")
    else:
        talk("Hey! It’s getting late, isn’t it? Good night!")

def get_input_method():
    talk("Hey! Wanna talk or type today?")
    talk("Type 'talk' if you wanna chat, or 'type' if you prefer typing.")
    while True:
        user_choice = input().lower()
        if user_choice == 'talk':
            talk("Awesome! Let’s chat. I'm all ears!")
            return 'speak'
        elif user_choice == 'type':
            talk("Great! You can start typing your commands.")
            return 'write'
        else:
            talk("Oops, I didn’t quite catch that. Type 'talk' or 'type' please!")

def take_command(input_method):
    if input_method == 'speak':
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            r.pause_threshold = 1
            audio = r.listen(source)
        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language='en-uk')
            print(f"You said: {query}\n")
        except Exception as e:
            print("Oops! I didn’t catch that. Could you say it again?")
            return "none"
        return query.lower()
    elif input_method == 'write':
        return input().lower()

def search_wikipedia(query):
    talk('Sure! Let me search Wikipedia for you...')
    query = query.replace("wikipedia", "")
    results = wikipedia.summary(query, sentences=3)
    talk("Here’s what I found:")
    talk(results)

def open_website(url):
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url  # Ensure the URL is complete
    webbrowser.open(url)

def get_random_from_file(file_path):
    with open(file_path, "rb") as file:
        data = pickle.load(file)
    return random.choice(data)

def get_quote():
    quotes_file = "quotes1.dat"
    quote = get_random_from_file(quotes_file)
    talk(quote)

def introduce_scyDroid():
    talk("Hey, I’m ScyDroid!")
    talk("S.C.Y.D.R.O.I.D stands for Smart Program for Advanced Resourceful Knowledge. Nice to meet you!")

def track_user_preferences(query):
    if 'joke' in query:
        user_preferences["jokes"] += 1
    elif 'quote' in query:
        user_preferences["quotes"] += 1
    elif 'wikipedia' in query:
        user_preferences["wikipedia"] += 1

    if sum(user_preferences.values()) > 5:
        favorite = max(user_preferences, key=user_preferences.get)
        talk(f"Hey, I’ve noticed you like {favorite} a lot! Want more of that?")

def set_reminder(reminder_text, delay_seconds):
    talk(f"Got it! I’ll remind you in {delay_seconds//60} minutes to {reminder_text}.")
    timer = Timer(delay_seconds, remind_user, [reminder_text])
    timer.start()

def remind_user(reminder_text):
    talk(f"Reminder: {reminder_text}")

def emotional_tone(query):
    happy_words = ['happy', 'good', 'excited', 'great']
    sad_words = ['sad', 'down', 'bad', 'tired']

    # Add more natural emotional tone responses without triggering explicitly
    if any(word in query for word in happy_words):
        talk("Oh, that’s awesome! It’s always great to hear you're feeling positive!")
    elif any(word in query for word in sad_words):
        talk("Oh no, I’m really sorry to hear that. You’ve got this, though! Let me know if I can help.")

def set_language():
    talk("Which language would you like me to use? I can speak English, Spanish, and French!")
    language_choice = take_command(input_method).lower()
    language_choice = fuzzy_match_language(language_choice)
    if language_choice:
        engine.setProperty('language', language_choice)
        talk(f"Okay, I’ll switch to {language_choice}. Let’s go!")
    else:
        talk("Sorry, I didn’t catch that. I’ll stick with English for now!")

def fuzzy_match_language(language_choice):
    languages = {
        "english": "en",
        "spanish": "es",
        "french": "fr",
        "german": "de",
        "italian": "it",
        "portuguese": "pt",
        "dutch": "nl"
    }

    for lang, code in languages.items():
        if fuzz.ratio(language_choice, lang) > 70:  # Tolerance for spelling mistakes
            return code
    return "en"  # Default to English if no match is found

def handle_open_website(query):
    if 'open' in query and 'website' in query:
        talk("Sure! What’s the website you want to open?")
        link = take_command(input_method)
        if 'http' not in link:
            if 'www' not in link:
                link = 'http://' + link  # Ensure the link starts with http://
            else:
                link = 'http://' + link  # If 'www' is present, but not http
        open_website(link)

def analyze_input(query):
    doc = nlp(query)
    for token in doc:
        if token.dep_ == "nsubj":
            return True
    return False

if __name__ == "__main__":
    load_responses()
    input_method = get_input_method()
    casual_greeting()

    print('''Functions:
          1. How are you
          2. Search in Wikipedia
          3. Open website
          4. Get quote
          5. Set reminder
          6. Exit/Stop''')

    while True:
        query = take_command(input_method)
        track_user_preferences(query)
        emotional_tone(query)
        if query in stored_responses:
            talk(stored_responses[query])
        elif 'how are you' in query or 'how are you doing' in query:
            talk("I’m doing great! Thanks for asking.")
        elif 'your day' in query:
            talk("I don't have days, but I’m always here for you!")
        elif 'who are you' in query or 'what is your name' in query:
            introduce_scyDroid()
        elif 'joke' in query:
            get_quote()
        elif 'wikipedia' in query:
            search_wikipedia(query)
        elif 'open website' in query:
            handle_open_website(query)
        elif 'learn' in query:
            learn_from_input(query)
        elif 'reminder' in query:
            set_reminder(query, 60)
        elif 'exit' in query or 'stop' in query:
            talk("Goodbye! Have a great day!")
            break
        else:
            learn_from_input(query)
