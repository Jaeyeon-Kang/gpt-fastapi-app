from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from openai import OpenAI
from prompt_template import make_prompt
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import faiss, numpy as np, csv, os, time
import pandas as pd
from utils.data_loader import load_chunks
import config # 설정 파일을 불러온다. 이제 하드코딩은 그만.
import PyPDF2
from docx import Document
import io

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

# ---------- 파일 업로드 처리 함수들 ─────────────────
def extract_text_from_file(file: UploadFile) -> str:
    """파일에서 텍스트를 추출합니다."""
    try:
        content = file.file.read()
        
        if file.filename.endswith('.txt'):
            return content.decode('utf-8')
        
        elif file.filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        
        elif file.filename.endswith('.docx'):
            doc = Document(io.BytesIO(content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        
        elif file.filename.endswith('.csv'):
            # CSV를 텍스트로 변환
            csv_text = content.decode('utf-8')
            return csv_text
        
        else:
            raise ValueError(f"지원하지 않는 파일 형식: {file.filename}")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"파일 처리 오류: {str(e)}")

def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list:
    """텍스트를 청크로 나눕니다."""
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    return text_splitter.split_text(text)

def rebuild_index(chunks: list) -> dict:
    """새로운 청크들로 FAISS 인덱스를 재구성합니다."""
    try:
        # 기존 청크 로드
        existing_chunks = load_chunks()
        
        # 새 청크 추가
        all_chunks = existing_chunks + chunks
        
        # 임베딩 생성
        print(f"🔄 {len(all_chunks)}개 청크의 임베딩을 생성하는 중...")
        embeddings = []
        for i, chunk in enumerate(all_chunks):
            if i % 10 == 0:
                print(f"진행률: {i}/{len(all_chunks)}")
            emb = client.embeddings.create(input=chunk, model=config.EMBED_MODEL).data[0].embedding
            embeddings.append(emb)
        
        embeddings = np.array(embeddings, dtype='float32')
        
        # FAISS 인덱스 생성
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)
        
        # 인덱스 저장
        faiss.write_index(index, config.INDEX_PATH)
        
        # 새 청크들을 텍스트 파일에 추가
        with open(config.TEXT_PATH, 'a', encoding='utf-8') as f:
            for chunk in chunks:
                f.write(chunk + '\n')
        
        return {
            "total_chunks": len(all_chunks),
            "new_chunks": len(chunks),
            "index_size_mb": os.path.getsize(config.INDEX_PATH) / (1024 * 1024)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"인덱스 재구성 오류: {str(e)}")

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

@app.post("/upload")
async def upload_files(
    files: list[UploadFile] = File(...),
    chunk_size: int = Form(512),
    chunk_overlap: int = Form(100)
):
    """파일을 업로드하고 RAG 시스템에 추가합니다."""
    try:
        start_time = time.time()
        
        if not files:
            raise HTTPException(status_code=400, detail="업로드할 파일이 없습니다.")
        
        all_chunks = []
        processed_files = 0
        
        for file in files:
            if not file.filename:
                continue
                
            # 파일 크기 제한 (10MB)
            if file.size > 10 * 1024 * 1024:
                raise HTTPException(status_code=400, detail=f"파일 크기가 너무 큽니다: {file.filename}")
            
            # 텍스트 추출
            text = extract_text_from_file(file)
            
            # 청킹
            chunks = chunk_text(text, chunk_size, chunk_overlap)
            all_chunks.extend(chunks)
            processed_files += 1
            
            print(f"✅ {file.filename} 처리 완료: {len(chunks)}개 청크 생성")
        
        if not all_chunks:
            raise HTTPException(status_code=400, detail="처리할 수 있는 텍스트가 없습니다.")
        
        # 인덱스 재구성
        index_info = rebuild_index(all_chunks)
        
        processing_time = time.time() - start_time
        
        return {
            "files_processed": processed_files,
            "chunks_created": len(all_chunks),
            "processing_time": round(processing_time, 2),
            "index_size": round(index_info["index_size_mb"], 2),
            "total_chunks": index_info["total_chunks"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"업로드 처리 중 오류 발생: {str(e)}")

@app.post("/add-text")
async def add_text_document(
    title: str = Form(...),
    content: str = Form(...),
    chunk_size: int = Form(512),
    chunk_overlap: int = Form(100)
):
    """텍스트를 직접 입력하여 RAG 시스템에 추가합니다."""
    try:
        start_time = time.time()
        
        # 입력 검증
        if not title or not title.strip():
            raise HTTPException(status_code=400, detail="문서 제목을 입력해주세요.")
        
        if not content or not content.strip():
            raise HTTPException(status_code=400, detail="문서 내용을 입력해주세요.")
        
        # 제목 길이 제한
        if len(title.strip()) > 200:
            raise HTTPException(status_code=400, detail="문서 제목이 너무 깁니다. 200자 이하로 입력해주세요.")
        
        # 텍스트 길이 제한 (1MB)
        content_bytes = content.encode('utf-8')
        if len(content_bytes) > 1024 * 1024:
            raise HTTPException(status_code=400, detail="텍스트가 너무 깁니다. 1MB 이하로 입력해주세요.")
        
        # 청킹 파라미터 검증
        if chunk_size < 100 or chunk_size > 2000:
            raise HTTPException(status_code=400, detail="청크 크기는 100-2000 사이여야 합니다.")
        
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise HTTPException(status_code=400, detail="청크 겹침은 0 이상이고 청크 크기보다 작아야 합니다.")
        
        # 청킹
        chunks = chunk_text(content, chunk_size, chunk_overlap)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="처리할 수 있는 텍스트가 없습니다.")
        
        # 인덱스 재구성
        index_info = rebuild_index(chunks)
        
        processing_time = time.time() - start_time
        
        # 로깅 개선
        print(f"✅ 텍스트 문서 처리 완료:")
        print(f"   - 제목: {title}")
        print(f"   - 청크 수: {len(chunks)}개")
        print(f"   - 처리 시간: {processing_time:.2f}초")
        print(f"   - 인덱스 크기: {index_info['index_size_mb']:.2f}MB")
        
        return {
            "title": title,
            "chunks_created": len(chunks),
            "processing_time": round(processing_time, 2),
            "index_size": round(index_info["index_size_mb"], 2),
            "total_chunks": index_info["total_chunks"],
            "content_size_bytes": len(content_bytes)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"텍스트 처리 중 오류 발생: {str(e)}")

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
        
        if 'cost_cents' in df.columns:
            df['cost_dollars'] = (df['cost_cents']).round(4)

        top_10 = df.nlargest(10, ['recall@5', 'f1']).to_dict(orient='records')

        summary = {
            "total_experiments": len(df),
            "best_recall": df['recall@5'].max(),
            "best_f1": df['f1'].max(),
            "avg_latency_ms": df['latency_ms'].mean(),
            "avg_cost": df['cost_dollars'].mean() if 'cost_dollars' in df.columns else df['cost_cents'].mean(),
            "perfect_scores": len(df[(df['recall@5'] == 1.0) & (df['f1'] == 1.0)])
        }
        
        # 브라우저가 응답을 캐싱하지 않도록 헤더 추가
        headers = {"Cache-Control": "no-cache, no-store, must-revalidate"}
        return JSONResponse(content={"summary": summary, "top_results": top_10}, headers=headers)

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="실험 결과 파일을 찾을 수 없습니다.")
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"결과 파일에서 필요한 열을 찾을 수 없습니다: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"결과 처리 중 오류 발생: {e}")

# ---------- 앱 시작 시 인덱스 확인 ─────────────────
ensure_faiss_index()

# ---------- 서버 실행 ─────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
