from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests
from dotenv import load_dotenv

load_dotenv()  # for local testing, no harm in production

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
headers = {
    "Authorization": f"Bearer {TOGETHER_API_KEY}",
    "Content-Type": "application/json"
}

TOGETHER_API_URL = "https://api.together.ai/v1/chat/completions"  # ✅ correct

MODEL = "mistralai/Mistral-7B-Instruct"

class Request(BaseModel):
    message: str

@app.post("/ask")
async def ask(request: Request):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": request.message}
        ]
    }

    try:
        response = requests.post(TOGETHER_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        choice = response.json()["choices"][0]
        return {"response": choice["message"]["content"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Together AI error: {str(e)}")



