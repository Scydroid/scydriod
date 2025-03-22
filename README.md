# ScyDroid AI - Virtual Assistant (Beta)

## 📌 Overview
ScyDroid is an advanced AI-powered virtual assistant that provides:
- **Information retrieval** (web search, question answering)
- **Task management** (reminders, scheduling, to-do lists)
- **Conversational AI** (free-flowing discussions, small talk, jokes)
- **Emotional support** (mood tracking, empathetic responses)
- **Voice interaction** (speech recognition & text-to-speech)
- **Machine learning-based intent classification**

ScyDroid leverages **NLTK, SpaCy, Scikit-Learn, Transformers, and SpeechRecognition** for advanced natural language processing.

⚠️ **This project is in Beta** – it is still under development and requires further improvements in accuracy, efficiency, and functionality.

---

## 📂 Required Files
Keep these files to ensure proper functioning:
1. **`scydroid.py`** - The main Python script containing ScyDroid's AI logic.
2. **`.scydroid/` (Generated at runtime)** - Stores logs, user preferences, cache, and knowledge base.
   - `responses.txt` - Stores predefined responses.
   - `interaction_logs.txt` - User interaction logs.
   - `advanced_knowledge_base.json` - AI's knowledge base.
   - `user_profile.json` - Stores user preferences.
   - `search_cache.json` - Cached web search results.
3. **`requirements.txt`** - Dependencies needed for the project (generate using `pip freeze > requirements.txt`).
4. **(Optional) `README.md`** - This documentation file.

---

## 💻 Hardware Requirements
To ensure smooth performance, your system should meet the following requirements:

### **Minimum Requirements:**
- **CPU**: Intel Core i3 (8th Gen) / AMD Ryzen 3
- **RAM**: 4GB
- **Storage**: 2GB free space
- **GPU**: Integrated Graphics (for basic processing)
- **OS**: Windows 10 / Linux (Ubuntu) / macOS

### **Recommended Requirements:**
- **CPU**: Intel Core i5 (10th Gen) / AMD Ryzen 5 or higher
- **RAM**: 8GB or more
- **Storage**: SSD with at least 5GB free space
- **GPU**: Dedicated GPU (NVIDIA GTX 1050 or higher) for faster AI processing
- **OS**: Windows 11 / Ubuntu 20.04+ / macOS Monterey+

---

## 🚀 Setup & Installation
### **1. Install Dependencies**
Ensure you have Python 3.8+ installed. Then, run:
```bash
pip install -r requirements.txt
```

### **2. Run ScyDroid**
```bash
python scydroid.py
```

---

## 🛠 Dependencies
Ensure the following Python packages are installed:
```bash
pip install numpy spacy nltk requests beautifulsoup4 transformers scikit-learn pyttsx3 speechrecognition
```

Additionally, download NLTK and SpaCy models:
```python
import nltk, spacy
nltk.download('wordnet')
nltk.download('punkt')
spacy.cli.download('en_core_web_sm')
```

---

## 🔧 Features & Functionalities
### ✅ **Natural Language Processing**
- Uses **SpaCy** for language understanding.
- Supports **sentiment analysis** and **question-answering** (DistilBERT).

### ✅ **Machine Learning-Based Intent Classification**
- Uses **TF-IDF Vectorization** + **MLPClassifier** to classify intents.

### ✅ **Voice Interaction**
- Speech recognition via **Google Speech API**.
- Text-to-speech via **pyttsx3**.

### ✅ **Contextual Conversations**
- Remembers conversation context (last topic, sentiment history).

### ✅ **Web Search & Knowledge Base**
- Integrates **BeautifulSoup & Requests** for fetching web results.
- Stores frequently asked information in a knowledge base.

---

## 🔥 Future Enhancements
- Improve **accuracy and response time**.
- Add **database support** (SQLite/PostgreSQL) for better persistence.
- Implement a **mobile/web UI**.
- Deploy as a **REST API** for cloud-based access.
- Integrate **LLM fine-tuning** for smarter responses.

---

## 📜 License
This project is open-source. Feel free to modify and enhance it!

---

## ❓ Need Help?
For any issues, open an **issue** on the repository or contact the developer.

---

