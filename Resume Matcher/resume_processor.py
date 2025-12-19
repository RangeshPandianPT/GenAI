"""
Resume Processor Module
Handles PDF extraction and resume parsing
"""
import PyPDF2
import os
import requests
import numpy as np
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
            # Handle the embedding response
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
            
            # Extract text from each page
            full_text = ""
            page_texts = []
            
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                full_text += page_text + "\n"
                page_texts.append({
                    'text': page_text,
                    'page_number': page_num + 1
                })
            
            return {
                "success": True,
                "text": full_text.strip(),
                "total_pages": total_pages,
                "page_texts": page_texts
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def process_resume(pdf_path, config):
    """
    Process a resume PDF - extract text and generate embedding
    """
    # Extract text
    extraction = extract_text_from_pdf(pdf_path)
    
    if not extraction["success"]:
        return extraction
    
    text = extraction["text"]
    
    # Generate embedding for the full resume text
    try:
        # Truncate text if too long (most embedding models have limits)
        max_chars = 8000
        embedding_text = text[:max_chars] if len(text) > max_chars else text
        
        embedding = get_embedding(embedding_text, config)
        
        return {
            "success": True,
            "text": text,
            "embedding": embedding,
            "total_pages": extraction["total_pages"],
            "filename": os.path.basename(pdf_path),
            "filepath": pdf_path,
            "char_count": len(text)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Embedding error: {str(e)}",
            "text": text
        }


def process_multiple_resumes(pdf_paths, config, progress_callback=None):
    """
    Process multiple resume PDFs
    """
    results = []
    total = len(pdf_paths)
    
    for idx, pdf_path in enumerate(pdf_paths):
        if progress_callback:
            progress_callback(idx + 1, total, os.path.basename(pdf_path))
        
        result = process_resume(pdf_path, config)
        result["index"] = idx
        results.append(result)
    
    return results


def parse_resume_sections(text):
    """
    Attempt to parse resume into sections based on common headers
    """
    sections = {
        "contact": "",
        "summary": "",
        "experience": "",
        "education": "",
        "skills": "",
        "projects": "",
        "certifications": "",
        "other": ""
    }
    
    # Common section headers
    section_keywords = {
        "contact": ["contact", "phone", "email", "address", "linkedin"],
        "summary": ["summary", "objective", "profile", "about"],
        "experience": ["experience", "work history", "employment", "career"],
        "education": ["education", "academic", "degree", "university", "college"],
        "skills": ["skills", "technical skills", "technologies", "competencies"],
        "projects": ["projects", "portfolio", "work samples"],
        "certifications": ["certifications", "certificates", "licenses", "credentials"]
    }
    
    lines = text.split('\n')
    current_section = "other"
    
    for line in lines:
        line_lower = line.lower().strip()
        
        # Check if this line is a section header
        for section, keywords in section_keywords.items():
            if any(kw in line_lower for kw in keywords) and len(line_lower) < 50:
                current_section = section
                break
        
        sections[current_section] += line + "\n"
    
    return sections
