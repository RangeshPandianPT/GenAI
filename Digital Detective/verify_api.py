import requests
try:
    response = requests.post(
        "http://localhost:8001/investigate",
        json={"username": "Neo_Hacker_99"}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Nodes Found: {len(response.json()['nodes'])}")
except Exception as e:
    print(f"Error: {e}")
