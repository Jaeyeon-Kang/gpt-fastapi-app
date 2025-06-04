# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import config
from prompt_template import make_prompt
from datetime import datetime
import os, csv

client = OpenAI(api_key=config.OPENAI_API_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    print("received body: ", body)

    prompt = body.get("prompt", "")
    system_role = body.get("system_role", "You are a helpful assistant.")
    temperature = body.get("temperature", 0.7)

    messages = make_prompt(prompt, system_role)

    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages,
        temperature=temperature,
    )

    print("✅ Using model:", response.model)

    reply = response.choices[0].message.content
    log_chat(
        timestamp=datetime.utcnow().isoformat(),
        user_input=prompt,
        system_role=system_role,
        temperature=temperature,
        reply=reply,
    )

    return {"reply": reply}


def log_chat(timestamp, user_input, system_role, temperature, reply):
    os.makedirs("logs", exist_ok=True)
    log_path = "logs/chat_logs.csv"
    log_exists = os.path.isfile(log_path)

    with open(log_path, "a", newline="", encoding="utf-8") as f:
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
