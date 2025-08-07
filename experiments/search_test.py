# search_test.py (수정된 버전)

import os
import openai
import faiss
import csv
import numpy as np
from dotenv import load_dotenv
from datetime import datetime

# 환경 변수 로드
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 경로 설정
INDEX_PATH = "data/index.faiss"
TEXT_PATH = "data/text_chunks.txt"
LOG_PATH = "logs/search_logs.csv"
EMBEDDING_MODEL = "text-embedding-3-small"

# 문단 불러오기
def load_text_chunks(path):
    with open(path, "r", encoding="utf-8") as f:
        return [chunk.strip() for chunk in f.read().split("\n\n") if chunk.strip()]

# 임베딩
def embed_text(text):
    response = openai.embeddings.create(
        input=text,
        model=EMBEDDING_MODEL
    )
    return np.array(response.data[0].embedding).astype("float32").reshape(1, -1)

def generate_gpt_answer(question, top_chunks):
    system_prompt = "다음 문단들을 참고하여 사용자의 질문에 명확하고 간결하게 답변해주세요."
    context = "\n\n".join(top_chunks)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{context}\n\n질문: {question}"}
    ]

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

# 검색 + 로그 저장
def search_similar(question, top_k=3):
    index = faiss.read_index(INDEX_PATH)
    chunks = load_text_chunks(TEXT_PATH)
    query_vec = embed_text(question)
    
    D, I = index.search(query_vec, top_k)
    top_chunks = [chunks [idx] for idx in I[0]]
    gpt_answer = generate_gpt_answer(question, top_chunks)

    print(f"\n🔍 질문: {question}")
    print(f"📎 Top-{top_k} 유사 문단 결과:\n")
    print("\n🧠 GPT 응답:")
    print(gpt_answer)
    print(query_vec.shape)  # → (1, 1536)
    print(query_vec[0][:5])  # → 첫 5차원만 출력해보기


    # 로그 데이터 구성
    log_entries = []
    timestamp = datetime.now().isoformat()

    for rank, (idx, score) in enumerate(zip(I[0], D[0]), 1):
        matched_chunk = chunks[idx]
        print(f"#{rank}")
        print(f"[거리: {score:.4f}]")
        print(matched_chunk)
        print("—" * 40)

        log_entries.append({
            "timestamp": timestamp,
            "question": question,
            "rank": rank,
            "chunk_index": idx,
            "distance": round(float(score), 4),
            "matched_text": matched_chunk.replace("\n", " ")
        })

    save_logs(log_entries)

# CSV 저장 함수
def save_logs(entries):
    fieldnames = ["timestamp", "question", "rank", "chunk_index", "distance", "matched_text"]
    file_exists = os.path.exists(LOG_PATH)

    with open(LOG_PATH, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for row in entries:
            writer.writerow(row)

if __name__ == "__main__":
    question = "GPT가 왜 중요한 기술인가요?"
    search_similar(question)


