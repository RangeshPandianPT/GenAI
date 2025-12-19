"""
Skill Extractor Module
Uses LLM to extract and categorize skills from text
"""
import requests
from config import get_api_config


def get_chat_response(messages, config):
    """Get chat response using the configured API"""
    if config["api_type"] == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=config["api_key"])
        response = client.chat.completions.create(
            model=config["chat_model"],
            messages=messages,
            temperature=0.3
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
    
    elif config["api_type"] == "huggingface":
        # Build prompt for Hugging Face models
        prompt = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt += f"<s>[INST] <<SYS>>\n{content}\n<</SYS>>\n\n"
            elif role == "user":
                prompt += f"{content} [/INST]"
        
        headers = {"Authorization": f"Bearer {config['api_key']}"}
        api_url = f"https://router.huggingface.co/hf-inference/models/{config['chat_model']}"
        
        response = requests.post(
            api_url,
            headers=headers,
            json={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 1024,
                    "temperature": 0.3,
                    "return_full_text": False
                },
                "options": {"wait_for_model": True}
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "")
            return str(result)
        else:
            raise Exception(f"Hugging Face API error: {response.status_code} - {response.text}")
    
    else:
        raise ValueError(f"Unknown API type: {config['api_type']}")


def extract_skills(text, config):
    """
    Extract skills from text using LLM
    Returns a dictionary with categorized skills
    """
    messages = [
        {
            "role": "system",
            "content": """You are a skill extraction expert. Extract all skills from the given text and categorize them.
            
Return ONLY a JSON object in this exact format (no markdown, no code blocks):
{
    "technical_skills": ["skill1", "skill2"],
    "soft_skills": ["skill1", "skill2"],
    "tools": ["tool1", "tool2"],
    "languages": ["lang1", "lang2"],
    "frameworks": ["framework1", "framework2"],
    "certifications": ["cert1", "cert2"]
}

Be thorough but precise. Normalize skill names (e.g., "JS" -> "JavaScript", "ML" -> "Machine Learning").
If a category has no skills, use an empty array."""
        },
        {
            "role": "user",
            "content": f"Extract all skills from this text:\n\n{text}"
        }
    ]
    
    try:
        response = get_chat_response(messages, config)
        
        # Clean up response - remove markdown code blocks if present
        response = response.strip()
        if response.startswith("```"):
            lines = response.split("\n")
            response = "\n".join(lines[1:-1])
        
        # Parse JSON
        import json
        skills = json.loads(response)
        
        # Ensure all categories exist
        default_skills = {
            "technical_skills": [],
            "soft_skills": [],
            "tools": [],
            "languages": [],
            "frameworks": [],
            "certifications": []
        }
        
        for key in default_skills:
            if key not in skills:
                skills[key] = []
        
        return skills
        
    except Exception as e:
        print(f"Error extracting skills: {e}")
        return {
            "technical_skills": [],
            "soft_skills": [],
            "tools": [],
            "languages": [],
            "frameworks": [],
            "certifications": [],
            "error": str(e)
        }


def extract_job_requirements(text, config):
    """
    Extract job requirements and categorize as required vs preferred
    """
    messages = [
        {
            "role": "system",
            "content": """You are a job requirement analyzer. Extract requirements from the job description.
            
Return ONLY a JSON object in this exact format (no markdown, no code blocks):
{
    "required_skills": ["skill1", "skill2"],
    "preferred_skills": ["skill1", "skill2"],
    "experience_years": "3-5",
    "education": "Bachelor's in Computer Science",
    "key_responsibilities": ["resp1", "resp2"]
}

Be thorough and precise. Normalize skill names."""
        },
        {
            "role": "user",
            "content": f"Extract requirements from this job description:\n\n{text}"
        }
    ]
    
    try:
        response = get_chat_response(messages, config)
        
        # Clean up response
        response = response.strip()
        if response.startswith("```"):
            lines = response.split("\n")
            response = "\n".join(lines[1:-1])
        
        import json
        requirements = json.loads(response)
        
        # Ensure all keys exist
        defaults = {
            "required_skills": [],
            "preferred_skills": [],
            "experience_years": "Not specified",
            "education": "Not specified",
            "key_responsibilities": []
        }
        
        for key in defaults:
            if key not in requirements:
                requirements[key] = defaults[key]
        
        return requirements
        
    except Exception as e:
        print(f"Error extracting job requirements: {e}")
        return {
            "required_skills": [],
            "preferred_skills": [],
            "experience_years": "Not specified",
            "education": "Not specified",
            "key_responsibilities": [],
            "error": str(e)
        }


def get_all_skills(skills_dict):
    """Flatten all skills from a skills dictionary into a single list"""
    all_skills = []
    for category in ["technical_skills", "soft_skills", "tools", "languages", "frameworks", "certifications"]:
        if category in skills_dict:
            all_skills.extend(skills_dict[category])
    return [s.lower() for s in all_skills]


def calculate_skill_match(resume_skills, job_requirements):
    """
    Calculate skill match percentage between resume and job requirements
    """
    resume_skills_flat = get_all_skills(resume_skills)
    
    required = [s.lower() for s in job_requirements.get("required_skills", [])]
    preferred = [s.lower() for s in job_requirements.get("preferred_skills", [])]
    
    # Calculate matches
    required_matches = []
    required_missing = []
    
    for skill in required:
        # Check for exact or partial match
        matched = any(skill in rs or rs in skill for rs in resume_skills_flat)
        if matched:
            required_matches.append(skill)
        else:
            required_missing.append(skill)
    
    preferred_matches = []
    for skill in preferred:
        matched = any(skill in rs or rs in skill for rs in resume_skills_flat)
        if matched:
            preferred_matches.append(skill)
    
    # Calculate scores
    required_score = len(required_matches) / len(required) * 100 if required else 100
    preferred_score = len(preferred_matches) / len(preferred) * 100 if preferred else 100
    
    # Weighted average (required skills are more important)
    total_score = (required_score * 0.7 + preferred_score * 0.3)
    
    return {
        "total_score": round(total_score, 2),
        "required_score": round(required_score, 2),
        "preferred_score": round(preferred_score, 2),
        "required_matches": required_matches,
        "required_missing": required_missing,
        "preferred_matches": preferred_matches,
        "total_required": len(required),
        "total_preferred": len(preferred)
    }
