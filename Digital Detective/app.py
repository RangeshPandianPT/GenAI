from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import networkx as nx
import asyncio
from typing import List, Dict, Any

from modules.github import GitHubModule
from modules.reddit import RedditModule
from modules.breaches import BreachModule

app = FastAPI(title="The Digital Detective")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# --- MODULE INITIALIZATION ---
# Instantiate modules once, they hold no state.
modules = [
    GitHubModule(),
    RedditModule(),
    # BreachModule not directly called on username right now, usually a secondary scan
]

# --- API ENDPOINTS ---

@app.post("/investigate", response_model=GraphResponse)
async def investigate_target(request: InvestigationRequest):
    """
    Initiates an investigation on a target username.
    Instantiates a private session graph to prevent data collision.
    """
    # 1. Create a fresh session-based graph
    G = nx.Graph()
    target = request.username
    logs = [f"Starting investigation for target: {target}"]
    
    # Add Target Node
    G.add_node(target, group="target", title="Primary Target")
    
    # 2. Run Modules Asynchronously
    logs.append(f"Dispatching scans to {len(modules)} active modules...")
    
    # Fire off all investigations concurrently using `asyncio.gather`
    tasks = [module.investigate(target) for module in modules]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 3. Process Results & Build Graph
    for i, module_results in enumerate(results):
        module_name = modules[i].__class__.__name__
        if isinstance(module_results, Exception):
            logs.append(f"Error in {module_name}: {str(module_results)}")
            continue
            
        if not module_results:
             logs.append(f"{module_name}: No findings.")
             continue
             
        logs.append(f"{module_name}: Found {len(module_results)} interesting artifacts.")
        
        for item in module_results:
            node_id = item["id"]
            
            # Prevent re-adding the exact same node unnecessarily
            if not G.has_node(node_id):
                 G.add_node(
                     node_id, 
                     group=item.get("type", "unknown"), 
                     title=item.get("info", ""), 
                     label=item.get("label", node_id)
                 )
                 
            # Determine connection point
            # If the artifact provided a source_id, link it there, otherwise link to the main target
            source_id = item.get("source_id", target)
            
            # Ensure the source node exists in the graph before adding edge
            if not G.has_node(source_id):
                # Fallback to main target if source is missing to prevent graph disconnection
                source_id = target 
                
            G.add_edge(source_id, node_id, label=item.get("relation", "linked_to"))

    # 4. Format Response for Vis.js
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
        
    logs.append("Investigation sweep complete.")
    
    return GraphResponse(nodes=nodes, edges=edges, logs=logs)

# Mount static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
