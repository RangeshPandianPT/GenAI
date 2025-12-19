# RAG System with Ollama/OpenAI API

A flexible Retrieval-Augmented Generation (RAG) system that works with both **Ollama** and **OpenAI** APIs.

## 🚀 Features

- **Multi-API Support**: Switch between Ollama and OpenAI easily
- **PDF Processing**: Extract and vectorize PDF documents
- **Semantic Search**: Find relevant content using vector similarity
- **Interactive Q&A**: Ask questions about your documents

## 📋 Prerequisites

### For Ollama (Recommended for local use)
1. Install Ollama from [https://ollama.ai](https://ollama.ai)
2. Pull the required models:
```bash
ollama pull nomic-embed-text
ollama pull llama3.2
```

### For OpenAI
1. Get an API key from [https://platform.openai.com](https://platform.openai.com)
2. Set environment variable:
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your-api-key-here"

# Linux/Mac
export OPENAI_API_KEY="your-api-key-here"
```

## 🔧 Installation

1. Install Python dependencies:
```bash
pip install faiss-cpu PyPDF2 numpy requests openai
```

## ⚙️ Configuration

Edit `config.py` to switch between APIs:

### Using Ollama (Default)
```python
API_TYPE = "ollama"
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"
OLLAMA_CHAT_MODEL = "llama3.2"
```

### Using OpenAI
```python
API_TYPE = "openai"
OPENAI_EMBEDDING_MODEL = "text-embedding-ada-002"
OPENAI_CHAT_MODEL = "gpt-3.5-turbo"
```

## 📖 Usage

### Step 1: Process your PDF
```bash
python pdf_vector.py
```

This will:
- Read your PDF file
- Create text chunks
- Generate embeddings
- Create a FAISS vector index
- Save to `vectors.index` and `chunks.pkl`

### Step 2: Ask Questions
```bash
python question_vector.py
```

Interactive commands:
- Ask any question about your PDF
- Type `info` to see database statistics
- Type `quit`, `exit`, `bye`, or `q` to exit

## 🔄 Switching APIs

To switch from Ollama to OpenAI (or vice versa):

1. **Edit** `config.py` and change `API_TYPE`
2. **Delete** the old vector database:
   ```bash
   # Windows
   del vectors.index chunks.pkl
   
   # Linux/Mac
   rm vectors.index chunks.pkl
   ```
3. **Re-run** `pdf_vector.py` to recreate embeddings
4. **Run** `question_vector.py` to ask questions

> ⚠️ **Important**: Different APIs create different embeddings, so you must recreate the vector database when switching APIs.

## 📁 File Structure

- `config.py` - API configuration (edit this to switch APIs)
- `pdf_vector.py` - PDF processing and vectorization
- `question_vector.py` - Interactive question answering
- `vectors.index` - FAISS vector database (auto-generated)
- `chunks.pkl` - Text chunks and metadata (auto-generated)

## 🐛 Troubleshooting

### Ollama not responding
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if needed
ollama serve
```

### Missing models
```bash
# List installed models
ollama list

# Install missing models
ollama pull nomic-embed-text
ollama pull llama3.2
```

### OpenAI API errors
- Check your API key is set correctly
- Verify your OpenAI account has credits
- Ensure API_TYPE is set to "openai" in config.py

### Vector database not found
- Run `pdf_vector.py` first to create the database
- Check that `vectors.index` and `chunks.pkl` exist

## 💡 Tips

- **Ollama** is free and runs locally (no API costs)
- **OpenAI** generally provides better quality responses but costs money
- You can use different models in Ollama (mistral, llama2, etc.)
- Adjust `CHUNK_SIZE` in config.py for different chunking strategies

## 📝 Example

```bash
# 1. Configure (edit config.py if needed)
# 2. Process PDF
python pdf_vector.py

# 3. Ask questions
python question_vector.py

❓ Your question: What is the main topic of this document?
🔍 Found 3 relevant chunks:
   Chunk 1: Score 0.845 (≈Page 1)
   Chunk 2: Score 0.812 (≈Page 2)
   Chunk 3: Score 0.789 (≈Page 1)
🤖 Answer: The main topic of this document is...
```

## 🎯 Performance

- **Ollama**: Slower but free, runs locally
- **OpenAI**: Faster and higher quality, requires API costs
- Processing speed depends on PDF size and number of chunks

## 📦 Dependencies

- `faiss-cpu`: Vector similarity search
- `PyPDF2`: PDF text extraction
- `numpy`: Array operations
- `requests`: API calls (Ollama)
- `openai`: OpenAI API client (optional)

## 🔐 Security

- Never commit API keys to version control
- Use environment variables for sensitive data
- Keep your Ollama instance local or secured
