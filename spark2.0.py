import os
import pickle
import random
import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser
import wikipedia

# Initialize text-to-speech engine
engine = pyttsx3.init()
def talk(text):
    print(text)
    engine.say(text)
    engine.runAndWait()

# Load stored responses or create an empty dictionary
stored_responses = {}
response_file_path = "responses.txt"

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

def learn_from_input(input_text):
    talk(f"I'm not sure how to respond to: '{input_text}'")
    new_response = take_command(input_method)
    stored_responses[input_text] = new_response
    save_responses()
    talk(f"Got it! I'll remember that when someone asks: '{input_text}'")

def casual_greeting():
    current_hour = datetime.datetime.now().hour
    if 5 <= current_hour < 12:
        talk("Good morning! What's up?")
    elif 12 <= current_hour < 17:
        talk("Hey there! Good afternoon!")
    elif 17 <= current_hour < 22:
        talk("Good evening! How's it going?")
    else:
        talk("Hey! Good night!")

def get_input_method():
    talk("Do you wanna talk or type today?")
    talk("Type 'talk' if you wanna chat, or 'type' if you wanna proceed typing.")
    while True:
        user_choice = input().lower()
        if user_choice == 'talk':
            talk("Awesome! Let's chat. Start talking.")
            return 'speak'
        elif user_choice == 'type':
            talk("Cool! You can proceed typing.")
            return 'write'
        else:
            talk("Hmm, not sure what you mean. Type 'talk' or 'type'.")

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
            print("Say that again, please...!")
            return "none"
        return query.lower()
    elif input_method == 'write':
        return input().lower()

def search_wikipedia(query):
    talk('Searching Wikipedia...')
    query = query.replace("wikipedia", "")
    results = wikipedia.summary(query, sentences=3)
    talk("According to Wikipedia")
    talk(results)

def open_website(url):
    webbrowser.open(url)

def get_random_from_file(file_path):
    with open(file_path, "rb") as file:
        data = pickle.load(file)
    return random.choice(data)

def get_quote():
    quotes_file = "quotes1.dat"
    quote = get_random_from_file(quotes_file)
    talk(quote)

def introduce_spark():
    talk("I am Spark.")
    talk("S.P.A.R.K stands for Smart Program for Advanced Resourceful Knowledge.")

if __name__ == "__main__":
    load_responses()
    input_method = get_input_method()
    casual_greeting()
    print('''Functions:
          1.how are you
          2.search in wikipedia
          3.open google
          4.get quote
          5.exit/stop''')
    while True:
        query = take_command(input_method)
        if query in stored_responses:
            talk(stored_responses[query])
        elif 'how are you' in query or 'how are you doing' in query:
            talk("I'm just a program, but thanks for asking!")
        elif 'your day' in query:
            talk("I don't have days, but I'm here to help you out!")
        elif 'wikipedia' in query:
            search_wikipedia(query)
        elif 'open' in query and 'google' in query:
            open_website("https://www.google.com/")
        elif 'quote' in query:
            get_quote()
        elif 'what is your name' in query or 'who are you' in query:
            introduce_spark()
        elif 'exit' in query or 'stop' in query:
            talk("Catch you later!")
            break
        else:
            learn_from_input(query)
