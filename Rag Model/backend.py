"""
Flask Backend for RAG System
Provides API endpoints for PDF processing and question answering
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import faiss
import PyPDF2
import numpy as np
import pickle
import os
import requests
from config import get_api_config, validate_config, get_embedding_dimension
from werkzeug.utils import secure_filename
import traceback

app = Flask(__name__, static_folder='static')
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Validate configuration
try:
    validate_config()
    config = get_api_config()
except Exception as e:
    print(f"⚠️ Configuration error: {e}")
    config = None


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_embedding(text, config):
    """Get embedding for text using the configured API"""
    if config["api_type"] == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=config["api_key"])
        response = client.embeddings.create(input=text, model=config["embedding_model"])
        return response.data[0].embedding
    
    elif config["api_type"] == "ollama":
        response = requests.post(
            f"{config['base_url']}/api/embeddings",
            json={"model": config["embedding_model"], "prompt": text}
        )
        if response.status_code == 200:
            return response.json()["embedding"]
        else:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
    
    else:
        raise ValueError(f"Unknown API type: {config['api_type']}")


def get_chat_response(messages, config):
    """Get chat response using the configured API"""
    if config["api_type"] == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=config["api_key"])
        response = client.chat.completions.create(
            model=config["chat_model"],
            messages=messages
        )
        return response.choices[0].message.content
    
    elif config["api_type"] == "ollama":
        prompt = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt += f"System: {content}\n\n"
            elif role == "user":
                prompt += f"User: {content}\n\n"
        
        response = requests.post(
            f"{config['base_url']}/api/generate",
            json={
                "model": config["chat_model"],
                "prompt": prompt,
                "stream": False
            }
        )
        if response.status_code == 200:
            return response.json()["response"]
        else:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
    
    else:
        raise ValueError(f"Unknown API type: {config['api_type']}")


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current API configuration"""
    if config:
        return jsonify({
            "success": True,
            "api_type": config["api_type"],
            "embedding_model": config.get("embedding_model", ""),
            "chat_model": config.get("chat_model", "")
        })
    else:
        return jsonify({"success": False, "error": "Configuration not loaded"}), 500


@app.route('/api/status', methods=['GET'])
def check_status():
    """Check if vector database exists"""
    db_exists = os.path.exists("vectors.index") and os.path.exists("chunks.pkl")
    
    if db_exists:
        try:
            with open("chunks.pkl", "rb") as f:
                data = pickle.load(f)
            return jsonify({
                "success": True,
                "database_exists": True,
                "total_chunks": len(data['chunks']),
                "total_pages": data['total_pages']
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "database_exists": False,
                "error": str(e)
            })
    else:
        return jsonify({
            "success": True,
            "database_exists": False
        })


@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    """Upload and process PDF file"""
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file provided"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"success": False, "error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": "Only PDF files are allowed"}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process PDF
        with open(filepath, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            total_pages = len(pdf_reader.pages)
            
            # Extract text
            page_texts = []
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                page_texts.append({
                    'text': page_text,
                    'page_number': page_num + 1
                })
            
            text = ''.join([p['text'] for p in page_texts])
        
        # Create chunks
        chunks = []
        chunk_metadata = []
        
        for i in range(0, len(text), 400):
            chunk_text = text[i:i + 500]
            chunks.append(chunk_text)
            
            estimated_page = min((i // (len(text) // total_pages)) + 1, total_pages)
            chunk_metadata.append({
                'start_pos': i,
                'estimated_page': estimated_page
            })
        
        # Get embeddings
        embeddings = []
        for chunk in chunks:
            embedding = get_embedding(chunk, config)
            embeddings.append(embedding)
        
        # Create FAISS index
        embeddings = np.array(embeddings)
        embedding_dim = config["embedding_dim"]
        index = faiss.IndexFlatIP(embedding_dim)
        index.add(embeddings.astype('float32'))
        
        # Save to files
        faiss.write_index(index, "vectors.index")
        with open("chunks.pkl", "wb") as f:
            pickle.dump({
                'chunks': chunks,
                'metadata': chunk_metadata,
                'total_pages': total_pages
            }, f)
        
        return jsonify({
            "success": True,
            "message": "PDF processed successfully",
            "total_pages": total_pages,
            "total_chunks": len(chunks),
            "filename": filename
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.route('/api/ask', methods=['POST'])
def ask_question():
    """Ask a question about the processed PDF"""
    data = request.get_json()
    question = data.get('question', '').strip()
    
    if not question:
        return jsonify({"success": False, "error": "No question provided"}), 400
    
    # Check if database exists
    if not os.path.exists("vectors.index") or not os.path.exists("chunks.pkl"):
        return jsonify({
            "success": False,
            "error": "Vector database not found. Please upload a PDF first."
        }), 404
    
    try:
        # Load data
        index = faiss.read_index("vectors.index")
        with open("chunks.pkl", "rb") as f:
            data = pickle.load(f)
        
        chunks = data['chunks']
        metadata = data['metadata']
        total_pages = data['total_pages']
        
        # Get question embedding
        query_embedding = get_embedding(question, config)
        query_vector = np.array(query_embedding).reshape(1, -1)
        
        # Search similar chunks
        scores, indices = index.search(query_vector.astype('float32'), 3)
        
        # Build context
        context_parts = []
        relevant_chunks = []
        
        for score, idx in zip(scores[0], indices[0]):
            chunk_text = chunks[idx]
            page_num = metadata[idx]['estimated_page']
            context_parts.append(f"[Page {page_num}]: {chunk_text}")
            relevant_chunks.append({
                "text": chunk_text[:200] + "...",
                "page": page_num,
                "score": float(score)
            })
        
        context = '\n\n'.join(context_parts)
        
        # Get answer
        messages = [
            {
                "role": "system",
                "content": f"You are answering questions about a {total_pages}-page document. When providing answers, mention page numbers when relevant. Be concise and helpful."
            },
            {
                "role": "user",
                "content": f"Context: {context}\n\nQuestion: {question}\n\nAnswer based on the context:"
            }
        ]
        
        answer = get_chat_response(messages, config)
        
        return jsonify({
            "success": True,
            "answer": answer,
            "relevant_chunks": relevant_chunks,
            "total_pages": total_pages
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.route('/api/clear', methods=['POST'])
def clear_database():
    """Clear the vector database"""
    try:
        if os.path.exists("vectors.index"):
            os.remove("vectors.index")
        if os.path.exists("chunks.pkl"):
            os.remove("chunks.pkl")
        
        return jsonify({
            "success": True,
            "message": "Database cleared successfully"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 RAG System Backend Server")
    print("=" * 60)
    if config:
        print(f"✓ API Type: {config['api_type'].upper()}")
        print(f"✓ Embedding Model: {config.get('embedding_model', 'N/A')}")
        print(f"✓ Chat Model: {config.get('chat_model', 'N/A')}")
    print(f"✓ Server: http://localhost:5000")
    print("=" * 60)
    print("\n🌐 Open http://localhost:5000 in your browser\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
