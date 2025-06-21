from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

app = FastAPI()

# ✅ CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use exact domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Use Falcon 7B Instruct Model
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
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

        # Safely get reply
        if isinstance(result, list) and "generated_text" in result[0]:
            reply = result[0]["generated_text"]
        else:
            reply = "AI did not return a valid response."

        return { "response": reply }

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Hugging Face error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
