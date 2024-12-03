import os
import pickle
import random
import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser
import wikipedia
from fuzzywuzzy import fuzz
import json
import time
from threading import Timer
import tkinter as tk
from tkinter import scrolledtext

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Initialize memory and preferences
stored_responses = {}
response_file_path = "responses.txt"
user_preferences = {"jokes": 0, "quotes": 0, "wikipedia": 0}
session_memory = {}
log_file_path = "interaction_logs.txt"

# Create the Tkinter window
root = tk.Tk()
root.title("ScyDroid Visualizer")
root.geometry("500x500")

# Create the text box for displaying logs and responses
log_display = scrolledtext.ScrolledText(root, width=60, height=20, wrap=tk.WORD)
log_display.pack(pady=10)

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

# Function to handle speech output and display in the GUI
def talk(text):
    print(text)
    engine.say(text)
    engine.runAndWait()
    log_display.insert(tk.END, f"ScyDroid: {text}\n")
    log_display.yview(tk.END)  # Auto-scroll to the latest message

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
        talk("I’m glad to hear you’re feeling good! Keep it up!")
    elif any(word in query for word in sad_words):
        talk("I’m sorry to hear you’re feeling down. Let me know if I can help!")

# Ensure necessary files exist and load responses
ensure_files_exist()
load_responses()

# Get input method and introduce ScyDroid
input_method = get_input_method()
introduce_scyDroid()

# Start the main loop for interaction
while True:
    query = take_command(input_method)
    if query == "none":
        continue

    log_interaction(query, "User: " + query)

    track_user_preferences(query)

    if 'joke' in query:
        talk("Sure, let me tell you a joke.")
        talk("Why don’t skeletons fight each other? They don’t have the guts!")

    elif 'quote' in query:
        get_quote()

    elif 'exit' in query or 'bye' in query:
        talk("Goodbye! Have a great day!")
        break

    elif 'search' in query or 'wikipedia' in query:
        search_wikipedia(query)

    elif 'open' in query:
        open_website(query)

    elif 'learn' in query:
        learn_from_input(query)

    elif 'log' in query:
        analyze_logs()

    elif 'reminder' in query:
        talk("What would you like me to remind you about?")
        reminder_text = take_command(input_method)
        talk("How many minutes from now should I remind you?")
        delay_minutes = int(take_command(input_method))
        set_reminder(reminder_text, delay_minutes * 60)

    else:
        talk("Sorry, I didn’t quite understand that. Can you ask again?")

