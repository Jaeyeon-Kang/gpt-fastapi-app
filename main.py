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

# 1) Load environment variables
load_dotenv()

# 2) Initialize OpenAI client
client = OpenAI(api_key=config.OPENAI_API_KEY)

# 3) Create FastAPI app and enable CORS
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4) Shared log function
def log_chat(timestamp, user_input, system_role, temperature, reply):
    os.makedirs("logs", exist_ok=True)
    log_path = "logs/chat_logs.csv"
    log_exists = os.path.isfile(log_path)
    with open(log_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["timestamp", "user_input", "system_role", "temperature", "reply"],
        )
        if not log_exists:
            writer.writeheader()
        writer.writerow(
            {
                "timestamp": timestamp,
                "user_input": user_input,
                "system_role": system_role,
                "temperature": temperature,
                "reply": reply,
            }
        )

# 5) Simple chat endpoint (unchanged)
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

# 6) Paths and model for semantic search
INDEX_PATH = "data/index.faiss"
TEXT_PATH = "data/text_chunks.txt"
EMBEDDING_MODEL = "text-embedding-3-small"

def load_text_chunks(path):
    with open(path, "r", encoding="utf-8") as f:
        return [chunk.strip() for chunk in f.read().split("\n\n") if chunk.strip()]

def embed_text(text):
    response = client.embeddings.create(input=text, model=EMBEDDING_MODEL)
    vec = response.data[0].embedding
    return np.array(vec, dtype="float32").reshape(1, -1)

# 7) Now accepts both temperature and system_prompt dynamically
def generate_gpt_answer(question, top_chunks, temperature, system_prompt):
    context = "\n\n".join(top_chunks)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{context}\n\n질문: {question}"},
    ]
    response = client.chat.completions.create(
        model="gpt-4-1106-preview", messages=messages, temperature=temperature
    )
    return response.choices[0].message.content.strip()

# 8) Semantic search + GPT endpoint, fully dynamic
@app.post("/search")
async def search(request: Request):
    body = await request.json()
    # extract dynamic parameters from client
    question = body.get("question", "")
    top_k = body.get("top_k", 3)
    temperature = body.get("temperature", 0.7)
    system_prompt = body.get(
        "system_prompt",
        "다음 문단들을 참고하여 사용자의 질문에 명확하고 간결하게 답변해주세요.",
    )

    # 1) Embed the question
    query_vec = embed_text(question)
    # 2) FAISS lookup
    index = faiss.read_index(INDEX_PATH)
    chunks = load_text_chunks(TEXT_PATH)
    distances, indices = index.search(query_vec, top_k)
    top_chunks = [chunks[i] for i in indices[0]]

    # 3) Generate answer with dynamic temperature & system_prompt
    gpt_answer = generate_gpt_answer(question, top_chunks, temperature, system_prompt)

    # optional: log the search as well
    # log_chat(
    #     timestamp=datetime.utcnow().isoformat(),
    #     user_input=question,
    #     system_role="semantic_search",
    #     temperature=temperature,
    #     reply=gpt_answer,
    # )

    # 4) Return everything, including the parameters actually used
    return {
        "question": question,
        "top_k": top_k,
        "temperature": temperature,
        "system_prompt": system_prompt,
        "top_chunks": [
            {"rank": rank + 1, "text": chunks[idx], "distance": float(distances[0][rank])}
            for rank, idx in enumerate(indices[0])
        ],
        "gpt_answer": gpt_answer,
    }