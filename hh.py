import pickle
import os

# Data to store
data = {
    "quotes": [
        "The only way to do great work is to love what you do. – Steve Jobs",
        "The best time to plant a tree was 20 years ago. The second best time is now. – Chinese Proverb",
        "It does not matter how slowly you go as long as you do not stop. – Confucius",
        "Success usually comes to those who are too busy to be looking for it. – Henry David Thoreau",
        "Don’t watch the clock; do what it does. Keep going. – Sam Levenson",
        "The future belongs to those who believe in the beauty of their dreams. – Eleanor Roosevelt",
        "Believe you can and you're halfway there. – Theodore Roosevelt",
        "Your time is limited, don’t waste it living someone else’s life. – Steve Jobs",
        "The only limit to our realization of tomorrow is our doubts of today. – Franklin D. Roosevelt",
        "The best way to predict the future is to create it. – Peter Drucker",
        "You miss 100% of the shots you don't take. – Wayne Gretzky",
        "In the end, it's not the years in your life that count. It's the life in your years. – Abraham Lincoln"
    ],
   
}

# Directory to store files
directory = "stored_data"
if not os.path.exists(directory):
    os.makedirs(directory)

# File paths
files = {
    "quotes": os.path.join(directory, "quotes1.dat")
}

# Save data to files
for key, file_path in files.items():
    with open(file_path, "wb") as file:
        pickle.dump(data[key], file)

print("Data saved successfully in separate files.")
