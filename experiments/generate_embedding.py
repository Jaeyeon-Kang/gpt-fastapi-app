# generate_embedding.py

import os
import openai
import faiss
import numpy as np
from dotenv import load_dotenv

# 환경 변수 로드 (OPENAI_API_KEY)
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 파일 경로
TEXT_PATH = "data/text_chunks.txt"
INDEX_PATH = "data/index.faiss"
EMBEDDING_MODEL = "text-embedding-3-small"

def get_text_chunks(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    # 문단 구분 기준: 제목 제외, 숫자. 또는 \n\n로 분리 가능
    return [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]

def get_embedding(text):
    response = openai.embeddings.create(
        input=text,
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding

def main():
    chunks = get_text_chunks(TEXT_PATH)
    print(f"✅ 문단 수: {len(chunks)}")

    embeddings = []
    for i, chunk in enumerate(chunks):
        print(f"🔹 [{i+1}] 임베딩 중: {chunk[:30]}...")
        embedding = get_embedding(chunk)
        embeddings.append(embedding)

    # numpy 배열로 변환
    embedding_matrix = np.array(embeddings).astype("float32")

    # FAISS 인덱스 생성
    dimension = len(embedding_matrix[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(embedding_matrix)
    faiss.write_index(index, INDEX_PATH)

    print(f"\n✅ FAISS 인덱스 생성 완료: {INDEX_PATH}")

if __name__ == "__main__":
    main()
