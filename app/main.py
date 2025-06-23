from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from together import Together
from dotenv import load_dotenv

load_dotenv()  # only useful for local testing

app = FastAPI()

# ✅ CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Together API client
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
client = Together(api_key=TOGETHER_API_KEY)

# ✅ Request body schema
class Request(BaseModel):
    message: str

# ✅ API endpoint
@app.post("/ask")
async def ask(request: Request):
    try:
      response = client.chat.completions.create(
    model="mistralai/Mistral-7B-Instruct",
    messages=[
        {"role": "user", "content": request.message}
    ]
)

        return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Together AI error: {str(e)}")




