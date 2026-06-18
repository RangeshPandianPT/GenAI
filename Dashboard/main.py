from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import socket

app = FastAPI(title="GenAI Central Dashboard")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

def is_port_open(port, host='127.0.0.1'):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0

@app.get("/api/health")
async def check_health():
    return {
        "digital_detective": is_port_open(8001),
        "mood_analyzer": is_port_open(8000),
        "rag_model": is_port_open(5000),
        "resume_matcher": is_port_open(8003)
    }

if __name__ == "__main__":
    # Serve the dashboard on port 8080
    uvicorn.run(app, host="0.0.0.0", port=8080)
