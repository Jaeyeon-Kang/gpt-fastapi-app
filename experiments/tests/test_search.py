import numpy as np
import pytest
import faiss
import openai
import os

# 환경 변수 세팅 (테스트용, 실제 키는 .env에서 가져와야 함)
openai.api_key = os.getenv("OPENAI_API_KEY", "sk-...dummy")

# 샘플 데이터 (진짜 짧게)
CHUNKS = [
    "인공지능은 인간의 지능을 모방하는 기술이다.",
    "고양이는 귀엽다.",
    "파이썬은 프로그래밍 언어다."
]

# 임베딩 함수 (실제 grid_run.py에서 가져온 것과 유사)
def get_embeddings(texts):
    # 실제론 openai API를 써야 하지만, 테스트에선 임의 벡터로 대체
    # (실제 테스트에선 mocking 필요)
    return np.random.rand(len(texts), 1536).astype('float32')

# 인덱스 생성
def create_faiss_index(embeddings):
    dim = embeddings.shape[1]
    idx = faiss.IndexFlatIP(dim)
    faiss.normalize_L2(embeddings)
    idx.add(embeddings)
    return idx

# 검색 함수
def search_similar_chunks(query, index, chunk_embeds, top_k=2):
    # query 임베딩 (여기도 실제론 openai 써야 함)
    q_emb = np.random.rand(1, chunk_embeds.shape[1]).astype('float32')
    faiss.normalize_L2(q_emb)
    D, I = index.search(q_emb, top_k)
    return I[0]

# --- 테스트 케이스 ---
def test_hit():
    embeds = get_embeddings(CHUNKS)
    idx = create_faiss_index(embeds)
    result_idx = search_similar_chunks("인공지능이 뭐야?", idx, embeds, top_k=2)
    # 0번 인덱스(인공지능 문장)가 top-k에 포함되어야 함
    assert 0 in result_idx

def test_miss():
    embeds = get_embeddings(CHUNKS)
    idx = create_faiss_index(embeds)
    result_idx = search_similar_chunks("이 프로젝트 만든 사람은 누구야?", idx, embeds, top_k=2)
    # 데이터에 없는 질문이므로, 0번(인공지능) 인덱스가 반드시 포함된다고 보장할 수 없음
    # 일단 top-k 결과가 2개인지만 체크
    assert len(result_idx) == 2 