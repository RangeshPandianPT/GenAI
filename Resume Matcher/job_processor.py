"""
Job Processor Module
Handles job description parsing and processing
"""
import PyPDF2
import os
import requests
from config import get_api_config


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
    
    elif config["api_type"] == "huggingface":
        import numpy as np
        # Use BAAI/bge-base-en-v1.5 - works for feature extraction
        url = "https://router.huggingface.co/hf-inference/models/BAAI/bge-base-en-v1.5"
        
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "inputs": text[:2000] if len(text) > 2000 else text
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list):
                if len(result) > 0 and isinstance(result[0], list):
                    return np.mean(result, axis=0).tolist()
                return result
            return result
        else:
            raise Exception(f"Hugging Face API error: {response.status_code} - {response.text}")
    
    else:
        raise ValueError(f"Unknown API type: {config['api_type']}")


def extract_text_from_pdf(pdf_path):
    """
    Extract text content from a PDF file
    """
    try:
        with open(pdf_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            total_pages = len(pdf_reader.pages)
            
            full_text = ""
            for page in pdf_reader.pages:
                full_text += page.extract_text() + "\n"
            
            return {
                "success": True,
                "text": full_text.strip(),
                "total_pages": total_pages
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def process_job_description(text_or_path, config, is_file=False):
    """
    Process a job description - from text or PDF file
    """
    # Get text content
    if is_file:
        if text_or_path.lower().endswith('.pdf'):
            extraction = extract_text_from_pdf(text_or_path)
            if not extraction["success"]:
                return extraction
            text = extraction["text"]
        else:
            # Read as text file
            try:
                with open(text_or_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            except Exception as e:
                return {"success": False, "error": str(e)}
    else:
        text = text_or_path
    
    # Generate embedding
    try:
        max_chars = 8000
        embedding_text = text[:max_chars] if len(text) > max_chars else text
        
        embedding = get_embedding(embedding_text, config)
        
        return {
            "success": True,
            "text": text,
            "embedding": embedding,
            "char_count": len(text)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Embedding error: {str(e)}",
            "text": text
        }


def parse_job_sections(text):
    """
    Parse job description into sections
    """
    sections = {
        "title": "",
        "company": "",
        "location": "",
        "description": "",
        "responsibilities": "",
        "requirements": "",
        "qualifications": "",
        "benefits": "",
        "other": ""
    }
    
    section_keywords = {
        "responsibilities": ["responsibilities", "what you'll do", "duties", "role"],
        "requirements": ["requirements", "must have", "required", "qualifications"],
        "qualifications": ["qualifications", "preferred", "nice to have", "bonus"],
        "benefits": ["benefits", "perks", "we offer", "compensation"]
    }
    
    lines = text.split('\n')
    current_section = "description"
    
    for line in lines:
        line_lower = line.lower().strip()
        
        for section, keywords in section_keywords.items():
            if any(kw in line_lower for kw in keywords) and len(line_lower) < 60:
                current_section = section
                break
        
        sections[current_section] += line + "\n"
    
    return sections
