import os
import base64
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import openai
from prompt import system_prompt

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="."), name="static")

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/")
async def get_index():
    with open("index.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.post("/api/chat")
async def chat(audio: UploadFile = File(...)):
    print("Transcribing audio...")
    # Save the uploaded audio file temporarily
    file_path = f"temp_{audio.filename}"
    with open(file_path, "wb") as f:
        f.write(await audio.read())
    
    # 1. Transcribe Audio (Whisper)
    with open(file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
    user_text = transcription.text
    os.remove(file_path)
    
    print("Fetching Response from AI...")
    # 2. Get AI Response
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ]
    )
    ai_response = completion.choices[0].message.content
    
    # 3. Convert Text to Speech
    print("Converting AI Response to Speech...")
    speech = client.audio.speech.create(
        model="tts-1",
        input=ai_response,
        voice="onyx",
    )
    # The image has instructions="Speak in an adventurous tone with Indian English Accent" but it is not standard in TTS-1.
    # Added to system prompt instead.
    
    audio_bytes = speech.content
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    
    return {
        "user_text": user_text,
        "ai_text": ai_response,
        "audio_b64": audio_b64
    }
