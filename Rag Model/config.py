"""
API Configuration for RAG System
Supports: OpenAI, Ollama, and other APIs
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Selection - Change this to switch between APIs
API_TYPE = os.getenv('API_TYPE', 'ollama')  # Options: "openai", "ollama"

# ========== OLLAMA Configuration ==========
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_EMBEDDING_MODEL = os.getenv('OLLAMA_EMBEDDING_MODEL', 'nomic-embed-text')
OLLAMA_CHAT_MODEL = os.getenv('OLLAMA_CHAT_MODEL', 'llama3.2')

# ========== OpenAI Configuration ==========
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_EMBEDDING_MODEL = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-ada-002')
OPENAI_CHAT_MODEL = os.getenv('OPENAI_CHAT_MODEL', 'gpt-3.5-turbo')

# ========== Embedding Dimensions ==========
EMBEDDING_DIMENSIONS = {
    "openai": 1536,
    "ollama": 768,  # nomic-embed-text uses 768 dimensions
}

# ========== Chunking Configuration ==========
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '500'))
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '100'))

def get_embedding_dimension():
    """Get the embedding dimension for the selected API"""
    return EMBEDDING_DIMENSIONS.get(API_TYPE, 1536)

def get_api_config():
    """Get the configuration for the selected API"""
    config = {
        "api_type": API_TYPE,
        "embedding_dim": get_embedding_dimension()
    }
    
    if API_TYPE == "openai":
        config["api_key"] = OPENAI_API_KEY
        config["embedding_model"] = OPENAI_EMBEDDING_MODEL
        config["chat_model"] = OPENAI_CHAT_MODEL
    elif API_TYPE == "ollama":
        config["base_url"] = OLLAMA_BASE_URL
        config["embedding_model"] = OLLAMA_EMBEDDING_MODEL
        config["chat_model"] = OLLAMA_CHAT_MODEL
    
    return config

def validate_config():
    """Validate the configuration"""
    if API_TYPE == "openai":
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set. Please set it in your environment variables.")
    elif API_TYPE == "ollama":
        print(f"✓ Using Ollama at {OLLAMA_BASE_URL}")
        print(f"✓ Embedding model: {OLLAMA_EMBEDDING_MODEL}")
        print(f"✓ Chat model: {OLLAMA_CHAT_MODEL}")
    else:
        raise ValueError(f"Unknown API_TYPE: {API_TYPE}. Use 'openai' or 'ollama'")
