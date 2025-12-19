# Resume Matcher 🎯

An AI-powered system that matches candidate resumes to job descriptions using semantic embeddings and LLM-based skill extraction.

![Resume Matcher](https://img.shields.io/badge/AI-Powered-blue) ![Python](https://img.shields.io/badge/Python-3.8+-green) ![Flask](https://img.shields.io/badge/Flask-3.0+-red)

## ✨ Features

- **📄 Resume Upload** - Upload single or multiple PDF resumes with drag-and-drop
- **📋 Job Description Input** - Paste text or upload PDF job descriptions
- **🤖 LLM Skill Extraction** - Automatically extract and categorize skills using AI
- **🔍 Semantic Matching** - Use embeddings for deep semantic similarity analysis
- **📊 Match Scoring** - Combined skill and semantic matching with detailed breakdowns
- **📈 Results Export** - Export match results as CSV or JSON
- **🎨 Modern UI** - Beautiful dark theme with glassmorphism design

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Ollama (recommended) or OpenAI API key

### Installation

1. **Navigate to the project directory:**
   ```bash
   cd "d:\GenAI\Resume Matcher"
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your API:**
   
   Edit the `.env` file to set your preferred API:
   
   ```env
   # For Ollama (default - free, local)
   API_TYPE=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_EMBEDDING_MODEL=nomic-embed-text
   OLLAMA_CHAT_MODEL=llama3.2
   
   # For OpenAI
   # API_TYPE=openai
   # OPENAI_API_KEY=your_api_key_here
   ```

4. **Start Ollama (if using Ollama):**
   ```bash
   # Make sure Ollama is running and has the required models
   ollama pull nomic-embed-text
   ollama pull llama3.2
   ```

5. **Run the application:**
   ```bash
   python backend.py
   ```

6. **Open in browser:**
   ```
   http://localhost:5001
   ```

## 📖 How It Works

```
┌─────────────┐     ┌─────────────┐
│   Resume    │     │     Job     │
│    PDFs     │     │ Description │
└──────┬──────┘     └──────┬──────┘
       │                   │
       ▼                   ▼
┌─────────────────────────────────┐
│      Text Extraction (PyPDF2)   │
└──────────────┬──────────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
┌─────────────┐  ┌─────────────┐
│   Skills    │  │  Embedding  │
│  Extraction │  │ Generation  │
│   (LLM)     │  │  (FAISS)    │
└──────┬──────┘  └──────┬──────┘
       │                │
       ▼                ▼
┌─────────────────────────────────┐
│         Match Scoring           │
│  Final = 0.6×Semantic + 0.4×Skill │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│      Ranked Results + Export    │
└─────────────────────────────────┘
```

## 📁 Project Structure

```
Resume Matcher/
├── backend.py           # Flask API server
├── config.py            # API configuration
├── resume_processor.py  # Resume PDF processing
├── job_processor.py     # Job description processing
├── skill_extractor.py   # LLM skill extraction
├── matcher.py           # Matching algorithm
├── requirements.txt     # Python dependencies
├── .env                 # Environment configuration
├── uploads/             # Uploaded files
│   ├── resumes/
│   └── jobs/
├── data/                # Processed data
└── static/              # Frontend files
    ├── index.html
    ├── styles.css
    └── script.js
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/config` | GET | Get API configuration |
| `/api/status` | GET | Check system status |
| `/api/upload/resume` | POST | Upload resume PDF(s) |
| `/api/upload/job` | POST | Upload job description PDF |
| `/api/job/text` | POST | Submit job description text |
| `/api/match` | POST | Run matching algorithm |
| `/api/resumes` | GET | List uploaded resumes |
| `/api/resumes/clear` | POST | Clear all resumes |
| `/api/job/clear` | POST | Clear job description |
| `/api/skills/extract` | POST | Extract skills from text |
| `/api/results/export` | GET | Export results (CSV/JSON) |

## ⚙️ Configuration

### Supported APIs

- **Ollama** (Default) - Free, runs locally
- **OpenAI** - Requires API key

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_TYPE` | API to use (`ollama` or `openai`) | `ollama` |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_EMBEDDING_MODEL` | Embedding model | `nomic-embed-text` |
| `OLLAMA_CHAT_MODEL` | Chat model | `llama3.2` |
| `OPENAI_API_KEY` | OpenAI API key | - |

## 📊 Scoring Algorithm

**Final Score = (Semantic Score × 0.6) + (Skill Score × 0.4)**

- **Semantic Score**: Cosine similarity between resume and job embeddings
- **Skill Score**: Percentage of required/preferred skills matched

## 🎨 Screenshots

The UI features:
- Modern dark theme with gradient accents
- Drag-and-drop file upload
- Real-time skill extraction preview
- Interactive results table with sorting
- Detailed candidate modal with skill breakdown

## 🛠️ Tech Stack

- **Backend**: Python, Flask, FAISS
- **AI**: OpenAI/Ollama, LangChain concepts
- **Frontend**: HTML5, CSS3, JavaScript
- **PDF Processing**: PyPDF2
- **Data**: NumPy, Pandas

## 📝 License

MIT License - feel free to use and modify!

---

Made with ❤️ RANGESHPANDIAN PT

