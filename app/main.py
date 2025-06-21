from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests

app = FastAPI()

# ✅ Allow frontend to access the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Hugging Face API setup
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/gpt2"
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

headers = {
    "Authorization": f"Bearer {HUGGINGFACE_TOKEN}",
    "Content-Type": "application/json"
}

class Request(BaseModel):
    message: str

@app.post("/ask")
async def ask(request: Request):
    payload = { "inputs": request.message }

    try:
        response = requests.post(HUGGINGFACE_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        # ✅ Extract generated text safely
        reply = result[0].get("generated_text", "No response generated.")
        return { "response": reply }

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Hugging Face error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")




