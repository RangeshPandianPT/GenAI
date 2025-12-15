# RAG System - Web Interface Setup Guide

## 🎨 What's New

A beautiful, modern web interface for your RAG system with:
- **Drag & Drop PDF Upload** - Simply drop your PDF files
- **Real-time Chat Interface** - Interactive Q&A with your documents
- **Responsive Design** - Works on all devices
- **Beautiful Animations** - Smooth, professional UI/UX
- **Progress Indicators** - Visual feedback for all operations
- **Dark Mode Theme** - Easy on the eyes

## 📁 File Structure

```
Rag Model/
├── backend.py              # Flask API server
├── config.py              # API configuration
├── pdf_vector.py          # CLI version (still available)
├── question_vector.py     # CLI version (still available)
├── requirements.txt       # All dependencies
├── static/
│   ├── index.html        # Main webpage
│   ├── styles.css        # Beautiful styling
│   └── script.js         # Frontend logic
└── uploads/              # Uploaded PDFs (auto-created)
```

## 🚀 Quick Start

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure API
Edit `config.py` and set your preferred API:

**For Ollama (Free, Local):**
```python
API_TYPE = "ollama"
```

**For OpenAI:**
```python
API_TYPE = "openai"
OPENAI_API_KEY = "your-api-key"
```

### Step 3: Start the Server
```bash
python backend.py
```

You'll see:
```
🚀 RAG System Backend Server
============================================================
✓ API Type: OLLAMA
✓ Embedding Model: nomic-embed-text
✓ Chat Model: llama3.2
✓ Server: http://localhost:5000
============================================================

🌐 Open http://localhost:5000 in your browser
```

### Step 4: Open in Browser
Navigate to: **http://localhost:5000**

## 🎯 How to Use

### 1️⃣ Upload a PDF
- Click "Browse Files" or drag & drop your PDF
- Wait for processing (you'll see a progress bar)
- The system creates embeddings automatically

### 2️⃣ Ask Questions
- Once processing is complete, the chat interface appears
- Type your question in the input box
- Press Enter or click the send button
- Get instant AI-powered answers!

### 3️⃣ View Relevant Sections
Each answer shows:
- The AI response
- Relevant document sections (with page numbers)
- Similarity scores

## 🎨 Features Showcase

### Drag & Drop Upload
- **Visual feedback** when dragging files
- **Progress bar** during processing
- **File validation** (PDF only, max 16MB)

### Interactive Chat
- **Real-time responses** from AI
- **Chat history** preserved during session
- **Typing indicators** while processing
- **Relevant chunks** shown with each answer

### Beautiful UI/UX
- **Glass morphism** design effects
- **Smooth animations** throughout
- **Responsive layout** for all screen sizes
- **Dark theme** optimized for reading

### Smart Notifications
- Success messages (green)
- Error messages (red)
- Warning messages (orange)
- Info messages (blue)

## 🔧 API Endpoints

The backend provides these REST API endpoints:

### `GET /api/config`
Returns current API configuration

### `GET /api/status`
Checks if vector database exists

### `POST /api/upload`
Uploads and processes PDF file
- Accepts: `multipart/form-data` with file
- Returns: Processing status and statistics

### `POST /api/ask`
Asks a question about the document
- Accepts: `{"question": "your question"}`
- Returns: Answer and relevant chunks

### `POST /api/clear`
Clears the vector database

## 🛠️ Customization

### Change Colors
Edit `static/styles.css` and modify the CSS variables:
```css
:root {
    --primary-color: #6366f1;    /* Main color */
    --secondary-color: #06b6d4;  /* Accent color */
    --dark-bg: #0f172a;          /* Background */
}
```

### Adjust Chunking
Edit `config.py`:
```python
CHUNK_SIZE = 500        # Characters per chunk
CHUNK_OVERLAP = 100     # Overlap between chunks
```

### Change Server Port
Edit `backend.py` (last line):
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Change port here
```

## 📱 Mobile Responsive

The interface automatically adapts to:
- Desktop computers (full layout)
- Tablets (optimized spacing)
- Mobile phones (stacked layout)

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port 5000 is available
netstat -ano | findstr :5000

# Kill process if needed (Windows)
taskkill /PID <PID> /F
```

### Ollama not responding
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve
```

### Upload fails
- Check file size (max 16MB)
- Ensure file is PDF format
- Check server logs for errors

### Chat not working
- Ensure PDF was uploaded successfully
- Check that `vectors.index` and `chunks.pkl` exist
- Verify API configuration is correct

## 💡 Pro Tips

1. **Better Accuracy**: Use smaller chunk sizes for detailed documents
2. **Faster Processing**: Use larger chunks for general documents
3. **Multiple Documents**: Clear database between different PDFs
4. **Local Development**: Use Ollama for free unlimited usage
5. **Production**: Use OpenAI for better quality responses

## 🔒 Security Notes

- Server runs on localhost by default (safe)
- To allow remote access, change host in `backend.py`
- Never commit API keys to version control
- Use environment variables for sensitive data
- Consider adding authentication for production

## 🚀 Production Deployment

For production use:

1. **Disable Debug Mode**
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

2. **Use Production Server**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend:app
```

3. **Add HTTPS** (use nginx or similar)

4. **Set Environment Variables**
```bash
export FLASK_ENV=production
export OPENAI_API_KEY=your-key
```

## 📊 Performance

**Typical Processing Times:**
- 10-page PDF: ~30 seconds (Ollama) / ~10 seconds (OpenAI)
- 50-page PDF: ~2 minutes (Ollama) / ~30 seconds (OpenAI)
- 100-page PDF: ~4 minutes (Ollama) / ~1 minute (OpenAI)

**Response Times:**
- Question processing: 2-10 seconds depending on API

## 🎓 CLI Version Still Available

The original command-line versions are still available:
```bash
# Process PDF (CLI)
python pdf_vector.py

# Ask questions (CLI)
python question_vector.py
```

## 📞 Support

If you encounter issues:
1. Check the server console for error messages
2. Check browser console (F12) for frontend errors
3. Verify all dependencies are installed
4. Ensure API configuration is correct

## 🎉 Enjoy!

You now have a fully functional, beautiful RAG system with a modern web interface!

Happy chatting with your documents! 📚✨
