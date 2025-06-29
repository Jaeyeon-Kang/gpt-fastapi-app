from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from prompt_template import make_prompt
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import faiss, numpy as np, csv, os

# ── 환경 및 클라이언트 ─────────────────────────────
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# ─────────────────────────────────────────────────

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

# ── 경로 상수 ──────────────────────────────────────
INDEX_PATH = "data/index.faiss"
TEXT_PATH  = "data/text_chunks.txt"
EMBED_MODEL = "text-embedding-3-small"
# ─────────────────────────────────────────────────

# ---------- 유틸 ----------
def log_chat(ts, user_input, role, temp, reply):
    os.makedirs("logs", exist_ok=True)
    path = "logs/chat_logs.csv"
    new  = not Path(path).exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f,
              ["timestamp","user_input","system_role","temperature","reply"])
        if new: w.writeheader()
        w.writerow({
            "timestamp": ts, "user_input": user_input,
            "system_role": role, "temperature": temp, "reply": reply
        })

def ensure_faiss_index():
    """index.faiss 가 없거나 text 파일이 새로 수정됐으면 자동 생성"""
    idx = Path(INDEX_PATH); txt = Path(TEXT_PATH)
    if (not idx.exists()) or (txt.stat().st_mtime > idx.stat().st_mtime):
        print("🔄  Re-building FAISS index …")
        from generate_embedding import load_chunks, build_index
        build_index(load_chunks())
        print("✅  index.faiss rebuilt")

def embed_text(text:str):
    emb = client.embeddings.create(input=text, model=EMBED_MODEL).data[0].embedding
    return np.asarray(emb, dtype="float32").reshape(1, -1)

def load_chunks():
    with open(TEXT_PATH, encoding="utf-8") as f:
        return [c.strip() for c in f.read().split("\n\n") if c.strip()]

# ---------- 라우트 ----------
@app.post("/chat")
async def chat(req: Request):
    body   = await req.json()
    prompt = body.get("prompt", "")
    role   = body.get("system_role", "You are a helpful assistant.")
    temp   = float(body.get("temperature", 0.7))

    messages = make_prompt(prompt, role)
    res  = client.chat.completions.create(
        model="gpt-4-1106-preview", messages=messages, temperature=temp
    )
    reply = res.choices[0].message.content
    log_chat(datetime.utcnow().isoformat(), prompt, role, temp, reply)
    return {"reply": reply}

@app.post("/search")
async def search(req: Request):
    body  = await req.json()
    q     = body.get("question", "")
    top_k = int(body.get("top_k", 3))
    temp  = float(body.get("temperature", 0.7))
    sys_p = body.get("system_prompt",
            "다음 문단들을 참고하여 사용자의 질문에 명확하고 간결하게 답변해주세요.")

    # 1) 임베딩 & 검색
    vec   = embed_text(q)
    index = faiss.read_index(INDEX_PATH)
    chunks= load_chunks()
    D,I   = index.search(vec, top_k)
    top_chunks = [chunks[i] for i in I[0]]

    # 2) GPT 요약
    ctx   = "\n\n".join(top_chunks)
    messages = [
        {"role":"system","content":sys_p},
        {"role":"user"  ,"content":f"{ctx}\n\n질문: {q}"}
    ]
    ans = client.chat.completions.create(
        model="gpt-4-1106-preview", messages=messages, temperature=temp
    ).choices[0].message.content.strip()

    return {
        "question": q, "top_k": top_k, "temperature": temp,
        "system_prompt": sys_p,
        "top_chunks": [
            {"rank": r+1, "text": chunks[i], "distance": float(D[0][r])}
            for r,i in enumerate(I[0])
        ],
        "gpt_answer": ans
    }

# ---------- 앱 시작 시 인덱스 확인 ----------
ensure_faiss_index()