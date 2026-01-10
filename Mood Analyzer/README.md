# 🎭 Mood Analyzer

A beautiful AI-powered sentiment analysis web application that detects the emotional tone of text using Hugging Face's Inference API.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- 🎯 **Real-time Sentiment Analysis** - Instantly analyze text for positive/negative emotions
- 📊 **Confidence Scores** - See detailed confidence percentages for each sentiment
- 🎨 **Beautiful UI** - Modern dark theme with glassmorphism and smooth animations
- ⚡ **Fast API** - Powered by FastAPI for lightning-fast responses
- 🤗 **Hugging Face** - Uses state-of-the-art NLP models

## 🚀 Quick Start

### 1. Clone & Navigate
```bash
cd "d:\GenAI\Mood Analyzer"
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Key
```bash
# Copy the example env file
copy .env.example .env

# Edit .env and add your Hugging Face API key
# Get your key from: https://huggingface.co/settings/tokens
```

### 5. Run the Application
```bash
python app.py
```

### 6. Open in Browser
Navigate to: **http://localhost:8000**

## 📁 Project Structure

```
Mood Analyzer/
├── app.py              # FastAPI backend server
├── static/
│   ├── index.html      # Main HTML page
│   ├── styles.css      # CSS styling
│   └── script.js       # Frontend JavaScript
├── requirements.txt    # Python dependencies
├── .env.example        # Environment template
├── .gitignore
└── README.md
```

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve the main UI |
| `/analyze` | POST | Analyze sentiment of text |
| `/health` | GET | Health check endpoint |

### Example API Request
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this amazing project!"}'
```

### Response
```json
{
  "sentiment": "POSITIVE",
  "confidence": 99.87,
  "emoji": "😊",
  "scores": {
    "POSITIVE": 99.87,
    "NEGATIVE": 0.13
  }
}
```

## 🎨 Screenshots

The app features a stunning dark theme with:
- Animated gradient background orbs
- Glassmorphism card effects
- Dynamic color themes based on sentiment
- Smooth micro-animations

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI
- **Frontend**: HTML5, CSS3, JavaScript
- **AI Model**: DistilBERT (via Hugging Face API)
- **Styling**: Custom CSS with CSS Variables

## 📝 License

MIT License - feel free to use this project for learning and development!

---

Made with ❤️ using Hugging Face 🤗 and FastAPI ⚡
