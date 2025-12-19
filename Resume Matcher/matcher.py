"""
Matcher Module
Handles embedding-based matching between resumes and job descriptions
"""
import numpy as np
import faiss
import pickle
import os
from config import get_api_config


def cosine_similarity(vec1, vec2):
    """
    Calculate cosine similarity between two vectors
    """
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)


def calculate_semantic_score(resume_embedding, job_embedding):
    """
    Calculate semantic similarity score between resume and job description
    Returns a score between 0 and 100
    """
    similarity = cosine_similarity(resume_embedding, job_embedding)
    # Convert from [-1, 1] to [0, 100]
    score = (similarity + 1) * 50
    return round(score, 2)


def match_single_resume(resume_data, job_data, skill_match_data=None):
    """
    Match a single resume against a job description
    Returns detailed match results
    """
    # Calculate semantic similarity
    semantic_score = calculate_semantic_score(
        resume_data["embedding"],
        job_data["embedding"]
    )
    
    # Get skill match score if available
    if skill_match_data:
        skill_score = skill_match_data.get("total_score", 50)
        skill_details = skill_match_data
    else:
        skill_score = 50  # Default if no skill analysis
        skill_details = {}
    
    # Calculate final weighted score
    # 60% semantic similarity, 40% skill match
    final_score = (semantic_score * 0.6) + (skill_score * 0.4)
    
    return {
        "resume_filename": resume_data.get("filename", "Unknown"),
        "final_score": round(final_score, 2),
        "semantic_score": semantic_score,
        "skill_score": skill_score,
        "skill_details": skill_details,
        "char_count": resume_data.get("char_count", 0)
    }


def match_multiple_resumes(resumes_data, job_data, skill_matches=None):
    """
    Match multiple resumes against a job description
    Returns sorted results by match score
    """
    results = []
    
    for idx, resume_data in enumerate(resumes_data):
        if not resume_data.get("success", False):
            results.append({
                "resume_filename": resume_data.get("filename", f"Resume {idx}"),
                "error": resume_data.get("error", "Processing failed"),
                "final_score": 0
            })
            continue
        
        # Get skill match for this resume if available
        skill_match = None
        if skill_matches and idx < len(skill_matches):
            skill_match = skill_matches[idx]
        
        match_result = match_single_resume(resume_data, job_data, skill_match)
        match_result["index"] = idx
        results.append(match_result)
    
    # Sort by final score descending
    results.sort(key=lambda x: x.get("final_score", 0), reverse=True)
    
    # Add ranking
    for rank, result in enumerate(results, 1):
        result["rank"] = rank
    
    return results


def create_resume_index(resumes_data, config):
    """
    Create a FAISS index from resume embeddings for fast searching
    """
    valid_resumes = [r for r in resumes_data if r.get("success", False)]
    
    if not valid_resumes:
        return None, []
    
    embeddings = np.array([r["embedding"] for r in valid_resumes]).astype('float32')
    
    # Create FAISS index
    embedding_dim = config["embedding_dim"]
    index = faiss.IndexFlatIP(embedding_dim)  # Inner product (cosine similarity for normalized vectors)
    
    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    
    return index, valid_resumes


def search_similar_resumes(job_embedding, index, resumes_data, top_k=10):
    """
    Search for most similar resumes to a job description
    """
    if index is None:
        return []
    
    query = np.array([job_embedding]).astype('float32')
    faiss.normalize_L2(query)
    
    k = min(top_k, len(resumes_data))
    scores, indices = index.search(query, k)
    
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < len(resumes_data):
            result = {
                "resume_filename": resumes_data[idx].get("filename", f"Resume {idx}"),
                "similarity_score": round(float(score) * 100, 2),  # Convert to percentage
                "index": int(idx)
            }
            results.append(result)
    
    return results


def save_match_results(results, filepath):
    """
    Save match results to a pickle file
    """
    with open(filepath, 'wb') as f:
        pickle.dump(results, f)


def load_match_results(filepath):
    """
    Load match results from a pickle file
    """
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    return None


def get_match_summary(results):
    """
    Generate a summary of match results
    """
    if not results:
        return {"total": 0, "message": "No results"}
    
    scores = [r.get("final_score", 0) for r in results if "error" not in r]
    
    if not scores:
        return {"total": len(results), "message": "All resumes failed processing"}
    
    return {
        "total": len(results),
        "processed": len(scores),
        "failed": len(results) - len(scores),
        "average_score": round(sum(scores) / len(scores), 2),
        "highest_score": max(scores),
        "lowest_score": min(scores),
        "above_80": len([s for s in scores if s >= 80]),
        "above_60": len([s for s in scores if s >= 60]),
        "below_40": len([s for s in scores if s < 40])
    }
