import os
import pickle
import random
import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser
import wikipedia
from fuzzywuzzy import fuzz  # For fuzzy string matching
import json
import time
from threading import Timer

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Initialize memory and preferences
stored_responses = {}
response_file_path = "responses.txt"
user_preferences = {"jokes": 0, "quotes": 0, "wikipedia": 0}
session_memory = {}
log_file_path = "interaction_logs.txt"

# Ensure necessary files exist
def ensure_files_exist():
    if not os.path.exists(response_file_path):
        with open(response_file_path, "w") as file:
            pass  # Create the responses.txt file if it doesn't exist

    if not os.path.exists(log_file_path):
        with open(log_file_path, "w") as file:
            pass  # Create the log file if it doesn't exist

    if not os.path.exists("quotes1.dat"):
        with open("quotes1.dat", "wb") as file:
            pickle.dump([], file)  # Initialize the quotes file as empty if it doesn't exist

    if not os.path.exists("recent_queries.json"):
        with open("recent_queries.json", "w") as file:
            json.dump([], file)  # Initialize the recent queries file if it doesn't exist

    if not os.path.exists("user_data.json"):
        with open("user_data.json", "w") as file:
            json.dump({}, file)  # Initialize user data if it doesn't exist


# Function to handle speech output
def talk(text):
    print(text)
    engine.say(text)
    engine.runAndWait()

# Load predefined responses from file
def load_responses():
    if os.path.exists(response_file_path):
        with open(response_file_path, "r") as file:
            for line in file:
                if "::" in line:
                    query, response = line.strip().split("::", 1)
                    stored_responses[query.lower()] = response

# Save responses to file
def save_responses():
    with open(response_file_path, "w") as file:
        for query, response in stored_responses.items():
            file.write(f"{query}::{response}\n")

# Log interactions for future reference
def log_interaction(query, response):
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{datetime.datetime.now()} - User: {query} - Assistant: {response}\n")

# Analyze logs to generate context-based responses
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

# Learn from new input and update responses
def learn_from_input(input_text):
    talk(f"Oops, I don't know how to respond to: '{input_text}'")
    talk("Can you help me out? What should I say when someone asks about that?")
    new_response = take_command(input_method)
    stored_responses[input_text] = new_response
    save_responses()
    talk(f"Yay, thanks! I’ll remember that for next time.")

# Casual greeting based on the time of day
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

# Get input method: either speak or type
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

# Take user command via speech or text input
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

# Search Wikipedia for the query
def search_wikipedia(query):
    talk('Sure! Let me search Wikipedia for you...')
    query = query.replace("wikipedia", "")
    results = wikipedia.summary(query, sentences=3)
    talk("Here’s what I found:")
    talk(results)

# Open a website in the browser
def open_website(url):
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    webbrowser.open(url)

# Get a random quote from the quotes file
def get_random_from_file(file_path):
    with open(file_path, "rb") as file:
        data = pickle.load(file)
    return random.choice(data)

def get_quote():
    quotes_file = "quotes1.dat"
    quote = get_random_from_file(quotes_file)
    talk(quote)

# Introduce the assistant
def introduce_scyDroid():
    talk("Hey, I’m ScyDroid!")
    talk("S.C.Y.D.R.O.I.D stands for Smart Program for Advanced Resourceful Knowledge. Nice to meet you!")

# Track user preferences based on interactions
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

# Set a reminder after a certain delay
def set_reminder(reminder_text, delay_seconds):
    talk(f"Got it! I’ll remind you in {delay_seconds // 60} minutes to {reminder_text}.")
    timer = Timer(delay_seconds, remind_user, [reminder_text])
    timer.start()

# Remind the user about a task
def remind_user(reminder_text):
    talk(f"Reminder: {reminder_text}")

# Handle emotional tone in conversations
def emotional_tone(query):
    happy_words = ['happy', 'good', 'excited', 'great']
    sad_words = ['sad', 'down', 'bad', 'tired']

    if any(word in query for word in happy_words):
        talk("Oh, that’s awesome! It’s always great to hear you're feeling positive!")
    elif any(word in query for word in sad_words):
        talk("Oh no, I’m really sorry to hear that. You’ve got this, though! Let me know if I can help.")

# Set language preference for the assistant
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

# Handle opening websites
def handle_open_website(query):
        if 'open' in query:
        website = query.split('open')[1].strip()
        open_website(website)

# Main interaction loop
ensure_files_exist()
load_responses()

input_method = get_input_method()  # Determine whether to take voice or text input
talk("How can I assist you today?")
while True:
    query = take_command(input_method)  # Capture the user's query
    if query == "none":
        continue

    track_user_preferences(query)

    if "exit" in query or "bye" in query:
        talk("Goodbye! Have a great day!")
        break

    elif "hello" in query or "hi" in query:
        casual_greeting()

    elif "name" in query or "who are you" in query:
        introduce_scyDroid()

    elif "learn" in query:
        talk("What should I learn?")
        new_query = take_command(input_method)
        if new_query:
            learn_from_input(new_query)

    elif "tell me a joke" in query or "joke" in query:
        talk("Why don't skeletons fight each other? They don't have the guts!")

    elif "quote" in query:
        get_quote()

    elif "wikipedia" in query:
        search_wikipedia(query)

    elif "remind" in query:
        talk("What do you want me to remind you about?")
        reminder = take_command(input_method)
        talk("How many minutes from now?")
        time_in_minutes = int(take_command(input_method))
        set_reminder(reminder, time_in_minutes * 60)

    elif "how are you" in query:
        emotional_tone(query)

    elif "logs" in query:
        talk(analyze_logs())

    elif "open website" in query:
        handle_open_website(query)

    else:
        response = stored_responses.get(query.lower())
        if response:
            talk(response)
        else:
            talk("Sorry, I don’t know how to respond to that.")
            learn_from_input(query)

    log_interaction(query, response if response else "Sorry, no response")
    time.sleep(1)  # Optional: Delay between interactions
