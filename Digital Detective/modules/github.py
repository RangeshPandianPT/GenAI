import httpx
from typing import List, Dict, Any
from .base import BaseModule

class GitHubModule(BaseModule):
    """Fetches public GitHub profile information."""
    
    async def investigate(self, target: str) -> List[Dict[str, Any]]:
        findings = []
        
        async with httpx.AsyncClient() as client:
            try:
                # GitHub REST API endpoint for user info
                response = await client.get(
                    f"https://api.github.com/users/{target}",
                    headers={"Accept": "application/vnd.github.v3+json"},
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Add GitHub Profile Node
                    profile_id = f"gh_{target}"
                    info_text = f"Name: {data.get('name', 'N/A')}\n"
                    info_text += f"Bio: {data.get('bio', 'N/A')}\n"
                    info_text += f"Public Repos: {data.get('public_repos', 0)}"
                    
                    findings.append({
                        "id": profile_id,
                        "type": "social",
                        "label": "GitHub",
                        "info": info_text,
                        "relation": "has_profile"
                    })
                    
                    # Check for website/blog
                    if blog := data.get("blog"):
                        findings.append({
                            "id": f"url_{target}_blog",
                            "type": "website",
                            "label": "Blog/Website",
                            "info": blog,
                            "relation": "authored_by",
                            "source_id": profile_id # Tie it to the github node
                        })
                        
                    # Check for Twitter username
                    if twitter := data.get("twitter_username"):
                        findings.append({
                            "id": f"tw_{target}",
                            "type": "social",
                            "label": "Twitter",
                            "info": f"@{twitter}",
                            "relation": "linked_account",
                            "source_id": profile_id
                        })
                        
            except httpx.RequestError as e:
                print(f"Error fetching GitHub profile for {target}: {e}")
                
        return findings
