import os
import pickle
import random
import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser
import wikipedia
from fuzzywuzzy import fuzz
import re
import time
from threading import Timer
from textblob import TextBlob  # For sentiment analysis
from apscheduler.schedulers.background import BackgroundScheduler  # For reminders
from googletrans import Translator  # For multilingual support
import json

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Initialize memory and preferences
stored_responses = {}
response_file_path = "responses.txt"
user_preferences = {"jokes": 0, "quotes": 0, "wikipedia": 0}
session_memory = {}
log_file_path = "interaction_logs.txt"
user_data_file = "user_data.json"

# Initialize the language translator
translator = Translator()

# Load user data
def load_user_data():
    if os.path.exists(user_data_file):
        with open(user_data_file, 'r') as file:
            return json.load(file)
    return {}

def save_user_data(user_data):
    with open(user_data_file, 'w') as file:
        json.dump(user_data, file)

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
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{datetime.datetime.now()} - User: {query} - Assistant: {response}\n")

def analyze_logs():
    if not os.path.exists(log_file_path):
        return "I haven't had enough conversations to understand you yet."

    with open(log_file_path, "r") as log_file:
        logs = log_file.readlines()
    
    query_frequency = {}
    for log in logs:
        query = log.split("-")[1].split(":")[1].strip()
        if query in query_frequency:
            query_frequency[query] += 1
        else:
            query_frequency[query] = 1
    
    most_frequent_query = max(query_frequency, key=query_frequency.get)
    return f"You often ask about {most_frequent_query}. Maybe I can help you more with that?"

def emotional_tone(query):
    sentiment = TextBlob(query).sentiment
    if sentiment.polarity > 0:
        talk("You seem happy today!")
    elif sentiment.polarity < 0:
        talk("I can sense some frustration, how can I help?")
    else:
        talk("I see you're neutral, let me know if you'd like to chat or ask anything!")

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
        url = 'http://' + url
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

if __name__ == "__main__":
    load_responses()
    user_data = load_user_data()  # Load user profile
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
        elif 'wikipedia' in query:
            search_wikipedia(query)
        elif 'quote' in query:
            get_quote()
        elif 'joke' in query:
            get_random_from_file("jokes1.dat")
        elif 'remind' in query:
            talk("What should I remind you about?")
            reminder_text = take_command(input_method)
            talk("How many minutes from now?")
            minutes = int(take_command(input_method))
            set_reminder(reminder_text, minutes * 60)
        elif 'exit' in query or 'stop' in query:
            talk("Goodbye! Have a great day!")
            break
        else:
            talk("Sorry, I didn't understand that. Could you repeat?")
        
        time.sleep(1)
