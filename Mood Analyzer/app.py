"""
Mood Analyzer - Sentiment Analysis API
Uses Hugging Face Inference API for sentiment analysis
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Mood Analyzer API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hugging Face API configuration - using new router endpoint
HF_API_URL = "https://router.huggingface.co/hf-inference/models/distilbert/distilbert-base-uncased-finetuned-sst-2-english"
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")


class TextInput(BaseModel):
    text: str


class SentimentResponse(BaseModel):
    sentiment: str
    confidence: float
    emoji: str
    scores: dict


def get_emoji_and_sentiment(label: str) -> tuple[str, str]:
    """Return emoji and normalized sentiment based on label"""
    # Map star ratings (nlptown model) to sentiment
    star_mapping = {
        "1 star": ("😢", "VERY NEGATIVE"),
        "2 stars": ("😞", "NEGATIVE"),
        "3 stars": ("😐", "NEUTRAL"),
        "4 stars": ("🙂", "POSITIVE"),
        "5 stars": ("😊", "VERY POSITIVE")
    }
    
    # Also handle uppercase labels
    label_lower = label.lower()
    if label_lower in star_mapping:
        return star_mapping[label_lower]
    
    # Fallback for standard sentiment labels
    sentiment_map = {
        "positive": ("😊", "POSITIVE"),
        "negative": ("😢", "NEGATIVE"),
        "neutral": ("😐", "NEUTRAL")
    }
    
    if label_lower in sentiment_map:
        return sentiment_map[label_lower]
    
    return ("🤔", label.upper())


@app.post("/analyze", response_model=SentimentResponse)
async def analyze_sentiment(input_data: TextInput):
    """Analyze sentiment of the given text using Hugging Face API"""
    
    if not input_data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    if not HF_API_KEY:
        raise HTTPException(status_code=500, detail="Hugging Face API key not configured")
    
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {"inputs": input_data.text}
    
    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Handle nested list response from HF API
        if isinstance(result, list) and len(result) > 0:
            if isinstance(result[0], list):
                scores = result[0]
            else:
                scores = result
        else:
            raise HTTPException(status_code=500, detail="Unexpected API response format")
        
        # Find the highest scoring sentiment
        top_sentiment = max(scores, key=lambda x: x["score"])
        raw_label = top_sentiment["label"]
        confidence = top_sentiment["score"]
        
        # Get emoji and normalized sentiment label
        emoji, sentiment_label = get_emoji_and_sentiment(raw_label)
        
        # Create scores dictionary
        scores_dict = {item["label"]: round(item["score"] * 100, 2) for item in scores}
        
        return SentimentResponse(
            sentiment=sentiment_label,
            confidence=round(confidence * 100, 2),
            emoji=emoji,
            scores=scores_dict
        )
        
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="API request timed out")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"API request failed: {str(e)}")


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Serve the main HTML page"""
    return FileResponse("static/index.html")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "api_configured": bool(HF_API_KEY)}


# --- New Features for Social Dashboard ---

import feedparser
import urllib.parse

@app.post("/analyze-feed")
async def analyze_feed(input_data: TextInput):
    """
    Fetch news headlines (optionally by topic) and analyze their sentiment.
    If input_data.text is empty, fetches top news. 
    Otherwise treats input_data.text as a search query.
    """
    if not HF_API_KEY:
        raise HTTPException(status_code=500, detail="Hugging Face API key not configured")

    # 1. Fetch Headlines
    query = input_data.text.strip()
    if query:
        # Google News Search RSS
        encoded_query = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    else:
        # Google News Top Stories RSS
        rss_url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
    
    feed = feedparser.parse(rss_url)
    
    if not feed.entries:
        return {"headlines": [], "stats": {}}

    # Limit to top 15 headlines to avoid API rate limits/timeouts
    entries = feed.entries[:15]
    headlines = [entry.title for entry in entries]
    
    # 2. Batch Analysis
    # Note: The specific HF model used earlier might not support large batches 
    # or might be slow. We will send requests in small chunks (e.g., 5 at a time)
    # or just one by one if necessary. Ideally, we send a list.
    
    # Let's try sending all as a list first (most efficient if supported)
    # If the model is finite-state, it might reject list. 
    # distilbert-base-uncased-finetuned-sst-2-english usually supports list.
    
    analyzed_results = []
    
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }

    # Analyze individually for reliability in this demo (prevents one fail breaking all)
    # In production, you'd want true batching.
    positive_count = 0
    neutral_count = 0
    negative_count = 0
    
    import asyncio
    
    # We'll use a simple loop for now, maybe parallelize slightly if needed
    for entry in entries:
        payload = {"inputs": entry.title}
        try:
            # We use a shorter timeout for batch items
            response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=5)
            if response.status_code == 200:
                result = response.json()
                 # Handle response format (nested list logic from before)
                if isinstance(result, list) and len(result) > 0:
                    if isinstance(result[0], list):
                        scores = result[0]
                    else:
                        scores = result
                    
                    top = max(scores, key=lambda x: x["score"])
                    label = top["label"]
                    score = top["score"]
                    
                    emoji, sentiment = get_emoji_and_sentiment(label)
                    
                    if sentiment == "POSITIVE":
                        positive_count += 1
                    elif sentiment == "NEGATIVE":
                        negative_count += 1
                    else:
                        neutral_count += 1
                        
                    analyzed_results.append({
                        "title": entry.title,
                        "link": entry.link,
                        "published": entry.published if hasattr(entry, 'published') else "",
                        "sentiment": sentiment,
                        "emoji": emoji,
                        "confidence": round(score * 100, 1)
                    })
        except Exception as e:
            # Skip failed items
            print(f"Error analyzing headline: {e}")
            continue
            
    # Calculate aggregate stats
    total = len(analyzed_results)
    stats = {
        "count": total,
        "positive": positive_count,
        "neutral": neutral_count,
        "negative": negative_count,
        "overall_mood": "NEUTRAL"
    }
    
    if total > 0:
        if positive_count > negative_count and positive_count > neutral_count:
            stats["overall_mood"] = "POSITIVE"
        elif negative_count > positive_count and negative_count > neutral_count:
            stats["overall_mood"] = "NEGATIVE"
    
    return {
        "headlines": analyzed_results,
        "stats": stats,
        "query": query if query else "Top Stories"
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
