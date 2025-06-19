from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for request body
class Message(BaseModel):
    message: str

# AI chat endpoint
@app.post("/ask")
def ask_ai(payload: Message):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": payload.message}]
        )
        answer = response.choices[0].message.content.strip()
        return {"response": answer}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}
@app.get("/")
def read_root():
    return {"message": "Welcome to JOE AI backend!"}


