from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import networkx as nx
import random
import time
from typing import List, Dict, Any

app = FastAPI(title="The Digital Detective")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory graph storage (per session typically, here global for demo)
# Using NetworkX allows for complex graph algorithms later
G = nx.Graph()

class InvestigationRequest(BaseModel):
    username: str

class NodeData(BaseModel):
    id: str
    label: str
    group: str  # user, social, email, crypto, ip, location
    title: str  # Tooltip

class EdgeData(BaseModel):
    from_: str
    to: str
    label: str

class GraphResponse(BaseModel):
    nodes: List[NodeData]
    edges: List[EdgeData]
    logs: List[str]

# --- MOCK OSINT LOGIC ---
# In a real app, these would be separate modules in `scrapers/`

def mock_github_check(username: str) -> List[Dict]:
    """Simulates checking GitHub for a username."""
    time.sleep(0.5) # Simulate network delay
    
    # Realism: Only "find" if username looks like a dev
    if "dev" in username or "hacker" in username or "coder" in username or username == "Neo_Hacker_99":
        return [
            {"type": "social", "id": f"gh_{username}", "label": "GitHub", "info": "Repo: 'Auto-Exploit-V2'"},
            {"type": "email", "id": f"email_{username}", "label": "Email", "info": f"{username}@protonmail.com"}
        ]
    return []

def mock_reddit_check(username: str) -> List[Dict]:
    """Simulates checking Reddit."""
    time.sleep(0.6)
    if "hacker" in username or "anon" in username or username == "Neo_Hacker_99":
         return [
            {"type": "social", "id": f"rd_{username}", "label": "Reddit", "info": "Active in r/netsec"},
            {"type": "crypto", "id": "btc_wallet_1A1zP1...", "label": "BTC Wallet", "info": "Found in post history"}
        ]
    return []

def mock_breach_check(email: str) -> List[Dict]:
    """Simulates checking data breaches for an email."""
    if "@protonmail" in email:
        return [
            {"type": "password", "id": "pass_hashed", "label": "Hash", "info": "MD5: 5f4dcc3b5aa765d61d8327deb882cf99"},
            {"type": "ip", "id": "ip_192.168.1.55", "label": "Last IP", "info": "Location: Russia (Proxy)"}
        ]
    return []

# --- API ENDPOINTS ---

@app.post("/investigate", response_model=GraphResponse)
async def investigate_target(request: InvestigationRequest):
    """
    Initiates an investigation on a target username.
    Clears old graph and builds a new one.
    """
    global G
    G.clear()
    
    target = request.username
    logs = [f"Starting investigation for target: {target}"]
    
    # 1. Add Target Node
    G.add_node(target, group="target", title="Primary Target")
    
    # 2. Run Modules
    findings = []
    
    # GitHub Module
    logs.append("Scanning GitHub...")
    gh_results = mock_github_check(target)
    for item in gh_results:
        G.add_node(item["id"], group=item["type"], title=item["info"], label=item["label"])
        G.add_edge(target, item["id"], label="found_on")
        logs.append(f"Found GitHub profile: {item['info']}")
        
        # Recursive check (if email found)
        if item["type"] == "email":
            email = item["info"]
            logs.append(f"Scanning breaches for {email}...")
            breach_results = mock_breach_check(email)
            for b_item in breach_results:
                G.add_node(b_item["id"], group=b_item["type"], title=b_item["info"], label=b_item["label"])
                G.add_edge(item["id"], b_item["id"], label="leaked_in")
                logs.append(f"Found breach data: {b_item['info']}")

    # Reddit Module
    logs.append("Scanning Reddit...")
    rd_results = mock_reddit_check(target)
    for item in rd_results:
        G.add_node(item["id"], group=item["type"], title=item["info"], label=item["label"])
        G.add_edge(target, item["id"], label="mentions")
        logs.append(f"Found Reddit activity: {item['info']}")

    # 3. Format Response for Vis.js
    nodes = []
    for node_id, attrs in G.nodes(data=True):
        nodes.append(NodeData(
            id=node_id,
            label=attrs.get("label", node_id),
            group=attrs.get("group", "unknown"),
            title=attrs.get("title", "")
        ))
        
    edges = []
    for u, v, attrs in G.edges(data=True):
        edges.append(EdgeData(
            from_=u,
            to=v,
            label=attrs.get("label", "")
        ))
        
    logs.append("Investigation complete.")
    
    return GraphResponse(nodes=nodes, edges=edges, logs=logs)

# Mount static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
