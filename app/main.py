from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

app = FastAPI()

# ✅ Allow frontend access (change "*" to domain in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ OpenRouter setup
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
}

class Request(BaseModel):
    message: str

@app.post("/ask")
async def ask(request: Request):
    payload = {
        "model": "mistralai/mistral-7b-instruct",  # ✅ Free model
        "messages": [
            {"role": "user", "content": request.message}
        ]
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        result = response.json()

        # ✅ Extract the AI's reply
        reply = result["choices"][0]["message"]["content"]
        return {"response": reply}

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"OpenRouter error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


