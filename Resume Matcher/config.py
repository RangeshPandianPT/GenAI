"""
API Configuration for Resume Matcher
Supports: OpenAI, Ollama, Hugging Face APIs
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Selection - Change this to switch between APIs
API_TYPE = os.getenv('API_TYPE', 'huggingface')  # Options: "openai", "ollama", "huggingface"

# ========== Hugging Face Configuration ==========
HF_API_KEY = os.getenv('HF_API_KEY', '')
HF_EMBEDDING_MODEL = os.getenv('HF_EMBEDDING_MODEL', 'BAAI/bge-small-en-v1.5')
HF_CHAT_MODEL = os.getenv('HF_CHAT_MODEL', 'mistralai/Mistral-7B-Instruct-v0.2')

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
    "huggingface": 768,  # BAAI/bge-base-en-v1.5 uses 768 dimensions
}

# ========== Processing Configuration ==========
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '500'))
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '100'))


def get_embedding_dimension():
    """Get the embedding dimension for the selected API"""
    return EMBEDDING_DIMENSIONS.get(API_TYPE, 384)


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
    elif API_TYPE == "huggingface":
        config["api_key"] = HF_API_KEY
        config["embedding_model"] = HF_EMBEDDING_MODEL
        config["chat_model"] = HF_CHAT_MODEL
        config["base_url"] = "https://router.huggingface.co/hf-inference"
    
    return config


def validate_config():
    """Validate the configuration"""
    if API_TYPE == "openai":
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set. Please set it in your .env file.")
    elif API_TYPE == "ollama":
        print(f"✓ Using Ollama at {OLLAMA_BASE_URL}")
        print(f"✓ Embedding model: {OLLAMA_EMBEDDING_MODEL}")
        print(f"✓ Chat model: {OLLAMA_CHAT_MODEL}")
    elif API_TYPE == "huggingface":
        if not HF_API_KEY:
            raise ValueError("HF_API_KEY is not set. Please set it in your .env file.")
        print(f"✓ Using Hugging Face API")
        print(f"✓ Embedding model: {HF_EMBEDDING_MODEL}")
        print(f"✓ Chat model: {HF_CHAT_MODEL}")
    else:
        raise ValueError(f"Unknown API_TYPE: {API_TYPE}. Use 'openai', 'ollama', or 'huggingface'")
