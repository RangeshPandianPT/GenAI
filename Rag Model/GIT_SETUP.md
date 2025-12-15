# Git Setup Guide

## 📦 Your project is now ready for Git!

### ✅ What's Been Set Up:

1. **`.env.example`** - Template for environment variables (COMMITTED)
2. **`.env`** - Your actual environment variables (IGNORED)
3. **`.gitignore`** - Excludes sensitive files (COMMITTED)
4. **`README_GIT.md`** - Project documentation for GitHub (COMMITTED)

### 🚀 Initialize Git Repository

```bash
# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: RAG System with web interface"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/your-repo.git

# Push to GitHub
git push -u origin main
```

### 🔐 Files EXCLUDED from Git (in .gitignore):

- ✅ `.env` (your API keys)
- ✅ `__pycache__/` (Python cache)
- ✅ `vectors.index` (generated database)
- ✅ `chunks.pkl` (generated chunks)
- ✅ `uploads/*.pdf` (uploaded PDFs)
- ✅ `.vscode/` (IDE settings)

### 📝 Files INCLUDED in Git:

- ✅ `.env.example` (template for others)
- ✅ `.gitignore` (git configuration)
- ✅ `requirements.txt` (dependencies)
- ✅ `backend.py` (Flask server)
- ✅ `config.py` (configuration loader)
- ✅ `static/` folder (HTML, CSS, JS)
- ✅ `README_GIT.md` (documentation)

### 🌟 For Others to Use Your Repo:

When someone clones your repo, they should:

```bash
# Clone
git clone <your-repo-url>
cd "Rag Model"

# Copy environment template
cp .env.example .env

# Edit .env with their API keys
# (Open .env and add their OPENAI_API_KEY or keep Ollama settings)

# Install dependencies
pip install -r requirements.txt

# Run the server
python backend.py
```

### 🔄 Future Updates:

```bash
# Check status
git status

# Add changes
git add .

# Commit
git commit -m "Your commit message"

# Push
git push
```

### ⚠️ IMPORTANT:

**NEVER commit your `.env` file!**
- It contains your API keys
- Already in `.gitignore`
- Others will create their own from `.env.example`

### ✨ You're Ready!

Your project is now:
- ✅ Git-ready
- ✅ Secure (API keys protected)
- ✅ Shareable
- ✅ Professional

Just run `git init` and push to GitHub! 🚀
