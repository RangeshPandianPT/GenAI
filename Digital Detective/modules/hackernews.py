import httpx
from typing import List, Dict, Any
from .base import BaseModule

class HackerNewsModule(BaseModule):
    """Investigates a target username on HackerNews."""
    
    async def investigate(self, target: str) -> List[Dict[str, Any]]:
        findings = []
        
        # Use HN Firebase API to get user profile
        url = f"https://hacker-news.firebaseio.com/v0/user/{target}.json"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    
                    if data:
                        # Found a HackerNews profile
                        findings.append({
                            "id": f"hn_{target}",
                            "type": "social",
                            "label": f"HN: {target}",
                            "info": f"Karma: {data.get('karma', 0)}\nCreated: {data.get('created', 'Unknown')}",
                            "relation": "has_account",
                            "source_id": target
                        })
                        
                        # Check if user has about text
                        about = data.get("about", "")
                        if about:
                            findings.append({
                                "id": f"hn_bio_{target}",
                                "type": "info",
                                "label": "HN Bio",
                                "info": str(about)[:100] + ("..." if len(str(about)) > 100 else ""),
                                "relation": "bio",
                                "source_id": f"hn_{target}"
                            })
            except Exception as e:
                # Log error quietly or append error finding if necessary
                pass
                
        return findings
