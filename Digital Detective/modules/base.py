from typing import List, Dict, Any

class BaseModule:
    """Base class for all OSINT gathering modules."""
    
    async def investigate(self, target: str) -> List[Dict[str, Any]]:
        """
        Investigate a target and return a list of findings.
        Returns empty list if no findings.
        
        Expected finding format:
        {
            "id": "unique_node_id",
            "type": "node_group_category", # e.g., 'social', 'email', 'crypto', 'ip'
            "label": "Short Label",
            "info": "Detailed tooltip info",
            "relation": "edge_label" # How it relates to the source (e.g., 'found_on', 'mentions')
        }
        """
        raise NotImplementedError("Modules must implement the investigate method.")
