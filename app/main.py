from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
from io import BytesIO
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask")
async def ask(request: Request):
    try:
        body = await request.json()
        user_message = body.get("message", "")

        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {TOGETHER_API_KEY}"
            },
            json={
                "model": "deepseek-ai/DeepSeek-V3",
                "messages": [
                    {"role": "user", "content": user_message}
                ]
            },
        )

        data = response.json()
        return {
            "response": data["choices"][0]["message"]["content"]
            if "choices" in data else "Something went wrong."
        }

    except Exception as e:
        return {"error": str(e)}

@app.post("/ask-pdf")
async def ask_about_pdf(file: UploadFile = File(...), question: str = Form(...)):
    try:
        contents = await file.read()

        if file.filename.endswith(".pdf"):
            reader = PdfReader(BytesIO(contents))
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        else:
            text = contents.decode("utf-8")

        prompt = f"Document:\n{text[:2000]}\n\nQuestion: {question}"

        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {TOGETHER_API_KEY}"
            },
            json={
                "model": "deepseek-ai/DeepSeek-V3",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
        )

        data = response.json()
        return {
            "response": data["choices"][0]["message"]["content"]
            if "choices" in data else "Something went wrong."
        }

    except Exception as e:
        return {"error": str(e)}
