from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
import requests

app = FastAPI()

# CORS for frontend compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask")
async def ask(request: dict):
    user_message = request.get("message", "")
    response = requests.post(
        "https://api.together.xyz/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer YOUR_TOGETHER_API_KEY"
        },
        json={
            "model": "deepseek-ai/DeepSeek-V3",  # or any available model
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

@app.post("/ask-pdf")
async def ask_about_pdf(file: UploadFile = File(...), question: str = Form(...)):
    contents = await file.read()

    # Handle PDF
    if file.filename.endswith(".pdf"):
        reader = PdfReader(file.file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    else:
        text = contents.decode("utf-8")

    # Combine question and extracted text
    prompt = f"Document:\n{text[:2000]}\n\nQuestion: {question}"

    response = requests.post(
        "https://api.together.xyz/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer YOUR_TOGETHER_API_KEY"
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



