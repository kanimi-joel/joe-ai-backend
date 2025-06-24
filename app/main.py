from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import fitz  # PyMuPDF
import os
import requests

app = FastAPI(
    title="JOE AI Backend",
    version="0.1.0",
    description="Chat + PDF-powered AI Assistant"
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
MODEL = "deepseek-ai/DeepSeek-V3"


# Pydantic model for JSON body in /ask
class AskRequest(BaseModel):
    message: str


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


@app.get("/")
def root():
    return {"message": "JOE AI backend is live and ready 🚀"}


@app.post("/ask")
async def ask(request: AskRequest):
    response = ask_openai(request.message)
    return {"response": response}


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
