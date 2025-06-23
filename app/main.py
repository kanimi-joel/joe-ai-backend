from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from together import Together
from dotenv import load_dotenv

# Load .env variables (useful for local testing)
load_dotenv()

app = FastAPI()

# ✅ CORS Middleware to allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend domain if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Together AI setup
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

if not TOGETHER_API_KEY:
    raise Exception("TOGETHER_API_KEY not found in environment")

client = Together(api_key=TOGETHER_API_KEY)

# ✅ Define input format
class Request(BaseModel):
    message: str

# ✅ POST endpoint
@app.post("/ask")
async def ask(request: Request):
    try:
        response = client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct",  # Fast & reliable model
            messages=[
                {"role": "user", "content": request.message}
            ]
        )
        return {"response": response.choices[0].message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Together AI error: {str(e)}")


