from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from openai import OpenAI
from prompt_template import make_prompt
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import faiss, numpy as np, csv, os
import pandas as pd
from utils.data_loader import load_chunks
import config # 설정 파일을 불러온다. 이제 하드코딩은 그만.

# ── 환경 및 클라이언트 ─────────────────────────────
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# ─────────────────────────────────────────────────

app = FastAPI()

# 정적 파일 서빙 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS 미들웨어 추가: 이제 보안을 조금 더 신경 쓴 설정으로.
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS, # config.py에 정의된 주소만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- 유틸리티 함수들 ───────────────────────
def log_chat(ts, user_input, role, temp, reply):
    os.makedirs(config.LOG_DIR, exist_ok=True)
    path = config.CHAT_LOG_PATH
    new  = not Path(path).exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, ["timestamp", "user_input", "system_role", "temperature", "reply"])
        if new: w.writeheader()
        w.writerow({
            "timestamp": ts, "user_input": user_input,
            "system_role": role, "temperature": temp, "reply": reply
        })

def ensure_faiss_index():
    """index.faiss 가 없거나 text 파일이 새로 수정됐으면 자동 생성."""
    idx_path = Path(config.INDEX_PATH)
    txt_path = Path(config.TEXT_PATH)
    if not idx_path.exists() or (txt_path.exists() and txt_path.stat().st_mtime > idx_path.stat().st_mtime):
        print("🔄 FAISS 인덱스를 다시 만드는 중... 잠시 기다려.")
        try:
            from experiments.generate_embedding import build_index
            chunks = load_chunks()
            build_index(chunks)
            print("✅ index.faiss 생성 완료.")
        except Exception as e:
            print(f"❌ Faiss 인덱스 생성 실패: {e}")

def embed_text(text: str):
    try:
        emb = client.embeddings.create(input=text, model=config.EMBED_MODEL).data[0].embedding
        return np.asarray(emb, dtype="float32").reshape(1, -1)
    except Exception as e:
        # OpenAI API에서 에러가 나면, 서버가 죽는 대신 클라이언트에게 알려준다.
        raise HTTPException(status_code=500, detail=f"임베딩 생성 오류: {e}")

# ---------- API 라우트 ─────────────────────────────
@app.get("/")
async def read_root():
    """루트 경로에서 index.html 파일을 서빙한다."""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        # 혹시라도 index.html이 없을 경우를 대비한 친절한 안내.
        raise HTTPException(status_code=404, detail="index.html 파일을 찾을 수 없습니다.")

@app.post("/search")
async def search(req: Request):
    """RAG 검색을 수행하고 GPT 답변과 참조 문서를 반환한다."""
    try:
        body  = await req.json()
        q     = body.get("question", "")
        top_k = int(body.get("top_k", 3))
        temp  = float(body.get("temperature", 0.7))
        sys_p = body.get("system_prompt", "다음 문단들을 참고하여 사용자의 질문에 명확하고 간결하게 답변해주세요.")

        if not q:
            raise HTTPException(status_code=400, detail="질문이 비어있습니다.")

        # 1. Retrieval
        vec = embed_text(q)
        index = faiss.read_index(config.INDEX_PATH)
        chunks = load_chunks()
        D, I = index.search(vec, top_k)
        top_chunks = [chunks[i] for i in I[0]]

        # 2. Generation
        ctx = "\n\n".join(top_chunks)
        messages = [
            {"role": "system", "content": sys_p},
            {"role": "user", "content": f"{ctx}\n\n질문: {q}"}
        ]
        res = client.chat.completions.create(model=config.CHAT_MODEL, messages=messages, temperature=temp)
        ans = res.choices[0].message.content.strip()

        return {
            "question": q,
            "top_k": top_k,
            "temperature": temp,
            "system_prompt": sys_p,
            "top_chunks": [
                {"rank": r + 1, "text": chunks[i], "distance": float(D[0][r])}
                for r, i in enumerate(I[0])
            ],
            "gpt_answer": ans
        }
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Faiss 인덱스 또는 텍스트 파일을 찾을 수 없습니다.")
    except Exception as e:
        # 이제 예상치 못한 에러가 나도 서버는 죽지 않는다.
        return JSONResponse(status_code=500, content={"message": f"서버 내부 오류: {e}"})

@app.get("/results")
async def get_results():
    """실험 결과 CSV 파일을 읽어 JSON으로 반환한다."""
    try:
        results_dir = Path("experiments/results")
        csv_files = sorted(results_dir.glob("grid_search_*.csv"), key=os.path.getmtime, reverse=True)
        if not csv_files:
            raise FileNotFoundError

        latest_csv = csv_files[0]
        df = pd.read_csv(latest_csv)
        
        # 실제 CSV 헤더에 맞게 열 이름 수정
        # 'Recall@5' -> 'recall@5'
        # 'F1 Score' -> 'f1'
        # 'Latency(ms)' -> 'latency_ms'
        # 'Cost($)' -> 'cost_cents' (단위가 센트이므로 달러로 변환 필요)
        
        # 소수점 둘째자리까지 반올림하고 달러로 변환
        if 'cost_cents' in df.columns:
            df['cost_dollars'] = (df['cost_cents']).round(4)

        # 상위 10개 결과 선택
        top_10 = df.nlargest(10, ['recall@5', 'f1']).to_dict(orient='records')

        # 전체 요약 정보 계산
        summary = {
            "total_experiments": len(df),
            "best_recall": df['recall@5'].max(),
            "best_f1": df['f1'].max(),
            "avg_latency_ms": df['latency_ms'].mean(),
            "avg_cost": df['cost_dollars'].mean() if 'cost_dollars' in df.columns else df['cost_cents'].mean(),
            "perfect_scores": len(df[(df['recall@5'] == 1.0) & (df['f1'] == 1.0)])
        }
        
        return {"summary": summary, "top_results": top_10}

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="실험 결과 파일을 찾을 수 없습니다.")
    except KeyError as e:
        # 특정 컬럼이 없을 때 발생하는 에러를 좀 더 명확하게 알려준다.
        raise HTTPException(status_code=500, detail=f"결과 파일에서 필요한 열을 찾을 수 없습니다: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"결과 처리 중 오류 발생: {e}")

# ---------- 앱 시작 시 인덱스 확인 ─────────────────
ensure_faiss_index()
