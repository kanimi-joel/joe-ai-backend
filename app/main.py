from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from together import Together
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

app = FastAPI()

# ✅ CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Together AI client
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
if not TOGETHER_API_KEY:
    raise Exception("TOGETHER_API_KEY not set")

client = Together(api_key=TOGETHER_API_KEY)

# ✅ Pydantic input schema
class Request(BaseModel):
    message: str

@app.post("/ask")
async def ask(request: Request):
    try:
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",  # ✅ Supported model
            messages=[
                {"role": "user", "content": request.message}
            ]
        )
        return {"response": response.choices[0].message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Together AI error: {str(e)}")

