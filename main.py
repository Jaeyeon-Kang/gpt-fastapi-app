# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import config
from prompt_template import make_prompt

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
    prompt = body.get("prompt", "")
    messages = make_prompt(prompt)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    print("✅ Using model:", response.model)  # 이 줄 추가

    return {"reply": response.choices[0].message.content}
