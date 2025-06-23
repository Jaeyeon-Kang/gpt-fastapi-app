
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import config
from prompt_template import make_prompt
from datetime import datetime
import os, csv
import numpy as np
import faiss
from dotenv import load_dotenv
load_dotenv() 

client = OpenAI(api_key=config.OPENAI_API_KEY)

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
        
@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "")
    system_role = body.get("system_role", "You are a helpful assistant.")
    temperature = body.get("temperature", 0.7)

    messages = make_prompt(prompt, system_role)
 
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages,
        temperature=temperature,
    )



    reply = response.choices[0].message.content
    log_chat(
        timestamp=datetime.utcnow().isoformat(),
        user_input=prompt,
        system_role=system_role,
        temperature=temperature,
        reply=reply,
    )

    return {"reply": reply}



INDEX_PATH = "data/index.faiss"
TEXT_PATH = "data/text_chunks.txt"
EMBEDDING_MODEL = "text-embedding-3-small"

def load_text_chunks(path):
    with open(path, "r", encoding="utf-8") as f:
        return [chunk.strip() for chunk in f.read().split("\n\n") if chunk.strip()]

def embed_text(text):
    embedding = client.embeddings.create(
        input=text,
        model=EMBEDDING_MODEL
    ).data[0].embedding
    return np.array(embedding).astype("float32").reshape(1, -1)

def generate_gpt_answer(question, top_chunks):
    system_prompt = "다음 문단들을 참고하여 사용자의 질문에 명확하고 간결하게 답변해주세요."
    context = "\n\n".join(top_chunks)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{context}\n\n질문: {question}"}
    ]
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

@app.post("/search")
async def search(request: Request):
    body = await request.json()
    question = body.get("question", "")
    top_k = body.get("top_k", 3)

    # 벡터 임베딩
    query_vec = embed_text(question)
    # FAISS 인덱스 로드
    index = faiss.read_index(INDEX_PATH)
    chunks = load_text_chunks(TEXT_PATH)
    D, I = index.search(query_vec, top_k)
    top_chunks = [chunks[idx] for idx in I[0]]
    gpt_answer = generate_gpt_answer(question, top_chunks)

    # 로그 저장 (옵션)
    # log_chat(datetime.utcnow().isoformat(), question, "semantic_search", 0.7, gpt_answer)

    # 결과 반환
    return {
        "question": question,
        "top_chunks": [
            {"rank": rank+1, "text": chunks[idx], "distance": float(D[0][rank])}
            for rank, idx in enumerate(I[0])
        ],
        "gpt_answer": gpt_answer
    }