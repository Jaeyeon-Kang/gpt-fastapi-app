
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI
from utils.prompt_engine import make_prompt
from pydantic import BaseModel
from datetime import datetime
import csv
import os

class ChatRequest(BaseModel):
    prompt: str
    system: str = "You are a helpful assistant"

LOG_PATH = "logs/chat_logs.csv"

load_dotenv()
client = OpenAI()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 로그 저장 함수
def log_chat(timestamp, user_input, system_role, temperature, reply):
    os.makedirs("logs", exist_ok=True)  # logs 폴더 없으면 생성

    log_exists = os.path.isfile(LOG_PATH)
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "timestamp", "user_input", "system_role", "temperature", "reply"
        ])
        if not log_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": timestamp,
            "user_input": user_input,
            "system_role": system_role,
            "temperature": temperature,
            "reply": reply
        })
        
@app.post("/chat")
async def chat(request: ChatRequest):
    prompt = request.prompt
    system_role = request.system
    temperature = 0.7

    messages = make_prompt(prompt, system_role)
 
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=temperature
    )
    
    reply = response.choices[0].message.content

    # 로그 저장
    log_chat(
        timestamp=datetime.utcnow().isoformat(),
        user_input=prompt,
        system_role=system_role,
        temperature=temperature,
        reply=reply
    )
    
    return {"reply": reply}
