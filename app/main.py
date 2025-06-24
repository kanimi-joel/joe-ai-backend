# app/main.py

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import fitz  # PyMuPDF
import os
import requests

# Initialize app
app = FastAPI(
    title="JOE AI Backend",
    version="0.1.0",
    description="Chat + PDF-powered AI Assistant"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment key (Together API or OpenAI)
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")  # set this in your Railway settings
MODEL = "deepseek-ai/DeepSeek-V3"  # You can change this to any model available on Together AI


# === Core AI helper ===
def ask_openai(prompt: str) -> str:
    try:
        res = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {TOGETHER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )
        result = res.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ AI error: {str(e)}"


# === Health Check ===
@app.get("/")
def root():
    return {"message": "JOE AI backend is live and ready 🚀"}


# === Handle chat messages ===
@app.post("/ask")
async def ask(message: str = Form(...)):
    response = ask_openai(message)
    return {"response": response}


# === Handle PDF upload and Q&A ===
@app.post("/ask-pdf")
async def ask_pdf(file: UploadFile = File(...), question: str = Form(...)):
    if file.content_type != "application/pdf":
        return JSONResponse(status_code=400, content={"error": "Only PDF files are supported."})

    try:
        content = await file.read()
        doc = fitz.open(stream=content, filetype="pdf")
        full_text = ""

        for page in doc:
            full_text += page.get_text()

        prompt = f"Based on this document:\n{full_text}\n\nAnswer this question: {question}"
        answer = ask_openai(prompt)
        return {"response": answer}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
