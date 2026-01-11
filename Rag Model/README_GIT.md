# RAG System - AI-Powered PDF Chat

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-green)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modern, beautiful web-based RAG (Retrieval-Augmented Generation) system that allows you to chat with your PDF documents using AI. Supports both **Ollama** (free, local) and **OpenAI** APIs.

## ✨ Features

- 🎨 **Beautiful Modern UI** - Glass morphism design with smooth animations
- 📤 **Drag & Drop Upload** - Easy PDF file upload
- 💬 **Interactive Chat** - Real-time Q&A with your documents
- 🔍 **Semantic Search** - Vector-based similarity search using FAISS
- 📊 **Progress Tracking** - Visual feedback for all operations
- 🤖 **Multi-API Support** - Switch between Ollama and OpenAI
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 🔒 **Secure** - Environment variables for API keys

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Ollama (for local AI) OR OpenAI API key

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd "Rag Model"
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup environment variables**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your configuration
# For Ollama: Set API_TYPE=ollama (default)
# For OpenAI: Set API_TYPE=openai and add your OPENAI_API_KEY
```

4. **Install Ollama (if using local AI)**
```bash
# Download from https://ollama.ai
# Pull required models:
ollama pull nomic-embed-text
ollama pull llama3.2
```

5. **Start the server**
```bash
python backend.py
```

6. **Open in browser**
```
http://localhost:5000
```

## 📖 Usage

1. **Upload a PDF** - Click "Browse Files" or drag & drop
2. **Wait for processing** - System creates embeddings automatically
3. **Ask questions** - Chat interface appears after processing
4. **Get answers** - AI provides answers with page references

## ⚙️ Configuration

Edit `.env` file to customize:

```env
# API Selection
API_TYPE=ollama              # or "openai"

# Ollama Settings
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_CHAT_MODEL=llama3.2

# OpenAI Settings (if using OpenAI)
OPENAI_API_KEY=your-api-key-here
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
OPENAI_CHAT_MODEL=gpt-3.5-turbo

# Server Settings
SERVER_PORT=5000
MAX_CONTENT_LENGTH=16777216  # 16MB

# Chunking Settings
CHUNK_SIZE=500
CHUNK_OVERLAP=100
```

## 📁 Project Structure

```
Rag Model/
├── backend.py              # Flask API server
├── config.py               # Configuration loader
├── .env                    # Environment variables (not in git)
├── .env.example            # Environment template
├── requirements.txt        # Python dependencies
├── static/
│   ├── index.html         # Frontend HTML
│   ├── styles.css         # Styling
│   └── script.js          # Frontend logic
├── uploads/               # Uploaded PDFs (gitignored)
├── vectors.index          # FAISS index (gitignored)
└── chunks.pkl             # Text chunks (gitignored)
```

## 🔄 Switching APIs

To switch between Ollama and OpenAI:

1. Edit `.env` and change `API_TYPE`
2. Delete old database files:
   ```bash
   rm vectors.index chunks.pkl
   ```
3. Restart the server
4. Re-upload your PDF

## 🛠️ Development

### Run in development mode
```bash
python backend.py
```

### Install new dependencies
```bash
pip install <package>
pip freeze > requirements.txt
```

## 🐛 Troubleshooting

**Server won't start?**
- Check if port 5000 is available
- Ensure all dependencies are installed

**Ollama not working?**
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve
```

**Upload fails?**
- Ensure file is PDF format
- Check file size (max 16MB)
- Verify disk space available

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [FAISS](https://github.com/facebookresearch/faiss) - Vector similarity search
- [Ollama](https://ollama.ai) - Local LLM inference
- [OpenAI](https://openai.com) - GPT models
- [Flask](https://flask.palletsprojects.com/) - Web framework

## 📞 Support

If you encounter any issues, please open an issue on GitHub.

---

Made with ❤️ using Flask & AI
