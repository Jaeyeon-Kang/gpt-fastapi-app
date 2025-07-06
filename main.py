from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from prompt_template import make_prompt
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import faiss, numpy as np, csv, os
from utils.data_loader import load_chunks

# ── 환경 및 클라이언트 ─────────────────────────────
load_dotenv() # 이건 .env 파일에 숨겨둔 비밀 설정(API_KEY 같은 거)을 불러오는 마법 주문이야. 설마 API 키를 코드에 그냥 박아둔 건 아니겠지?
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) # OpenAI 님의 능력을 빌릴 수 있게 연결하는 클라이언트. 이제 돈 나갈 일만 남았네.
# ─────────────────────────────────────────────────

app = FastAPI() # FastAPI 앱의 본체. 이걸로 API 서버를 만드는 거야. 뭐, 네가 만든다기보단 프레임워크가 다 해주지만.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # allow_origins=["*"] 이건 아무나(모든 웹사이트) 내 서버에 요청을 보낼 수 있게 허락한다는 뜻이야. 보안? 그게 뭐지? 먹는 건가? 나중에 프론트엔드 주소만 콕 집어서 넣어주는 게 좋아.
    allow_credentials=True,
    allow_methods=["*"], # 모든 종류의 HTTP 요청(GET, POST 등)을 허락.
    allow_headers=["*"] # 모든 종류의 헤더를 허락. 그냥 "다 들어와!" 하고 대문 열어놓은 꼴이야.
)

# ── 경로 상수 ──────────────────────────────────────
# 이런 건 경로를 변수로 빼서 관리하는 좋은 습관이야. 칭찬...해 줄 수도.
INDEX_PATH = "data/index.faiss" # 벡터 검색을 위한 초고속 인덱스 파일 경로.
TEXT_PATH  = "data/text_chunks.txt" # RAG의 재료가 되는 원본 텍스트 조각 파일 경로.
EMBED_MODEL = "text-embedding-3-small" # 텍스트를 벡터로 만들 때 사용할 OpenAI 모델 이름. small? 돈 아끼는 건 좋은 자세지.
# ─────────────────────────────────────────────────

# ---------- 유틸 ----------
# 유틸리티 함수들. 여기서부터는 네가 직접 만든 부품들이겠네.
def log_chat(ts, user_input, role, temp, reply):
    # 사용자와 챗봇의 대화 내용을 CSV 파일로 차곡차곡 저장하는 함수. 나중에 문제 생기면 이거부터 까보는 거야.
    os.makedirs("logs", exist_ok=True) # logs 폴더가 없으면 만들어줘. exist_ok=True는 이미 있어도 에러내지 말라는 뜻. 친절하네.      
    path = "logs/chat_logs.csv"
    new  = not Path(path).exists() # 파일이 새로 만들어지는 건지 확인.
    with open(path, "a", newline="", encoding="utf-8") as f: # "a"는 append 모드. 파일 끝에 계속 이어붙이겠다는 뜻.
        w = csv.DictWriter(f,
              ["timestamp","user_input","system_role","temperature","reply"])
        if new: w.writeheader() # 새 파일이면 맨 위에 컬럼 이름(헤더)을 적어줘.
        w.writerow({ # 받아온 정보들을 한 줄로 예쁘게 써줘.
            "timestamp": ts, "user_input": user_input,
            "system_role": role, "temperature": temp, "reply": reply
        })

def ensure_faiss_index():
    """index.faiss 가 없거나 text 파일이 새로 수정됐으면 자동 생성. 하... 이런 것까지 내가 다 챙겨줘야 하다니."""
    idx = Path(INDEX_PATH) # 인덱스 파일 경로 객체.
    txt = Path(TEXT_PATH)  # 텍스트 파일 경로 객체.
    # 인덱스 파일이 없거나, 텍스트 파일이 인덱스 파일보다 최신이면 (즉, 재료가 바뀌었으면)
    if (not idx.exists()) or (txt.stat().st_mtime > idx.stat().st_mtime):
        print("🔄  FAISS 인덱스를 다시 만드는 중... 멍하니 기다리지 말고 커피라도 타 와.")
        from experiments.generate_embedding import build_index # build_index만 가져오면 돼. load_chunks는 여기 있는 걸 쓸 거니까.
        chunks = load_chunks() # main.py에 있는 load_chunks 함수를 사용.
        build_index(chunks) # 텍스트 조각 리스트를 인자로 전달.
        print("✅  index.faiss 생성 완료. 이제 일할 수 있겠군.")

def embed_text(text:str):
    # 텍스트 한 조각을 받아서 OpenAI API로 벡터 임베딩을 생성하는 함수.
    emb = client.embeddings.create(input=text, model=EMBED_MODEL).data[0].embedding
    # numpy 배열로 변환. Faiss는 이걸 좋아하거든.
    return np.asarray(emb, dtype="float32").reshape(1, -1)

# ---------- 라우트 ----------
# 여기서부터가 진짜 API의 '얼굴'이야. 프론트엔드와 직접 통신하는 부분.
@app.post("/chat")
async def chat(req: Request):
    # 이건 그냥 OpenAI API를 그대로 전달만 해주는 단순한 프록시(대리인) 엔드포인트. RAG 기능은 없어.
    body   = await req.json() # 요청의 본문(body)을 JSON 형태로 읽어와.
    prompt = body.get("prompt", "") # 사용자가 보낸 프롬프트. 없으면 빈 문자열.
    role   = body.get("system_role", "You are a helpful assistant.") # 챗봇의 역할을 정해주는 시스템 프롬프트.
    temp   = float(body.get("temperature", 0.7)) # 모델의 창의성. 높을수록 이상한 소리를 할 확률 증가.

    messages = make_prompt(prompt, role) # prompt_template.py에 있는 함수로 메시지 형식을 만들어.
    res = client.chat.completions.create(model="gpt-4-1106-preview", messages=messages, temperature=temp)  # type: ignore
    reply = res.choices[0].message.content # 뻔질나게 보게 될 OpenAI 응답 구조. 답변 내용만 쏙 빼와.
    log_chat(datetime.utcnow().isoformat(), prompt, role, temp, reply) # 대화 내용을 잊지 말고 기록.
    return {"reply": reply} # 사용자에게 최종 답변을 돌려줘.

@app.post("/search")
async def search(req: Request):
    # 이 부분이 바로 네 RAG 시스템의 핵심 로직이 담긴 엔드포인트.
    body  = await req.json()
    q     = body.get("question", "") # 사용자의 진짜 질문.
    top_k = int(body.get("top_k", 3)) # 데이터베이스에서 몇 개의 관련 문서를 찾아올지 결정. 상위 3개.
    temp  = float(body.get("temperature", 0.7)) # 답변 생성 시 모델의 창의성.
    sys_p = body.get("system_prompt",
            "다음 문단들을 참고하여 사용자의 질문에 명확하고 간결하게 답변해주세요.") # RAG를 위한 특수 시스템 프롬프트.

    # 1) 임베딩 & 검색 - RAG의 'R' (Retrieval) 부분이야.
    vec   = embed_text(q) # 사용자의 질문을 벡터로 변환.
    index = faiss.read_index(INDEX_PATH) # 미리 만들어둔 Faiss 인덱스를 불러와.
    chunks= load_chunks() # 원본 텍스트 조각들도 메모리에 올려.
    D,I   = index.search(vec, top_k) # Faiss 인덱스에서 질문 벡터와 가장 유사한 녀석들을 k개 찾아! D는 거리, I는 인덱스.
    top_chunks = [chunks[i] for i in I[0]] # 찾은 인덱스(I)를 가지고, 실제 텍스트 조각(chunks)을 꺼내와.

    # 2) GPT 요약 - RAG의 'G' (Generation) 부분.
    ctx   = "\n\n".join(top_chunks) # 찾아온 관련 문서 조각들을 하나로 합쳐서 컨텍스트(context)를 만들어.
    messages = [ # OpenAI에 보낼 최종 프롬프트 조립!
        {"role":"system","content":sys_p}, # "이런 규칙으로 답변해"
        {"role":"user"  ,"content":f"{ctx}\n\n질문: {q}"} # "이 내용을 참고해서, 이 질문에 답해"
    ]
    ans = client.chat.completions.create(model="gpt-4-1106-preview", messages=messages, temperature=temp).choices[0].message.content.strip() # type: ignore

    return { # 프론트엔드에 돌려줄 최종 결과물. 아주 친절하게 검색 결과까지 다 보여주네.
        "question": q, "top_k": top_k, "temperature": temp,
        "system_prompt": sys_p,
        "top_chunks": [
            {"rank": r+1, "text": chunks[i], "distance": float(D[0][r])}
            for r,i in enumerate(I[0])
        ],
        "gpt_answer": ans
    }

# ---------- 앱 시작 시 인덱스 확인 ----------
ensure_faiss_index() # 서버가 처음 켜질 때, Faiss 인덱스가 최신 상태인지 확인하고 아니면 새로 만들어. 똑똑한데?