import os
import csv
import itertools
import re
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 이 스크립트는 design 문서에 정의된 실험을 수행합니다.

# ─── 설정 (design 문서와 동기화) ──────────────────────────────────
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 실험 파라미터 그리드
CHUNK_STRATEGIES = ["S-A", "S-B", "S-C"]
TOP_K_VALUES = [3, 5, 8]
TEMPERATURE_VALUES = [0.2, 0.5, 0.8]

# 질문 샘플 (인공지능 주제 기준, 한국어) - 테스트용으로 더 축소
QUESTION_SAMPLES = {
    "fact": [
        "'인공지능'이라는 용어를 처음 만든 사람은 누구인가?"
    ],
    "summary": [],
    "creative": []
}

# 결과 저장 경로 (항상 프로젝트 루트 기준 experiments/results/에 저장되게 절대경로로 지정)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "experiments", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_CSV_PATH = os.path.join(RESULTS_DIR, f"grid_search_{TIMESTAMP}.csv")

# ─── 핵심 로직 (실제 구현) ─────────────────────────────────────────

def get_chunks_by_strategy(strategy: str, text: str):
    """지정된 전략에 따라 텍스트를 조각내는 함수"""
    print(f"Applying chunking strategy: {strategy}")
    
    if strategy == "S-A":
        # 문단 기준 분할 (빈 줄로 구분된 문단)
        chunks = [chunk.strip() for chunk in text.split('\n\n') if chunk.strip()]
        return chunks
    
    elif strategy == "S-B":
        # 고정 토큰 크기 분할 (약 500 토큰)
        encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 토크나이저
        tokens = encoding.encode(text)
        
        chunk_size = 500
        overlap = 50
        chunks = []
        
        for i in range(0, len(tokens), chunk_size - overlap):
            chunk_tokens = tokens[i:i + chunk_size]
            chunk_text = encoding.decode(chunk_tokens)
            if chunk_text.strip():
                chunks.append(chunk_text.strip())
        
        return chunks
    
    elif strategy == "S-C":
        # 재귀적 문자 분할 (LangChain 사용)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = text_splitter.split_text(text)
        return chunks
    
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

def get_question_type(question: str) -> str:
    """질문의 유형을 판별하는 함수"""
    if any(keyword in question for keyword in ["누구", "언제", "무엇", "어디", "어떤"]):
        return "fact"
    elif any(keyword in question for keyword in ["요약", "간략", "설명"]):
        return "summary"
    else:
        return "creative"

def run_single_experiment(chunk_strategy, question, top_k, temperature):
    """단일 실험을 실행하고 결과를 반환하는 함수"""
    try:
        # 1. 텍스트 파일 읽기 (상대 경로 수정)
        with open("../data/text_chunks.txt", "r", encoding="utf-8") as f:
            text = f.read()
        
        # 2. 청킹 전략 적용
        chunks = get_chunks_by_strategy(chunk_strategy, text)
        
        # 3. 간단한 키워드 기반 검색 (실제로는 Faiss 사용해야 함)
        question_lower = question.lower()
        relevant_chunks = []
        
        for chunk in chunks:
            # 질문의 키워드가 청크에 포함되어 있는지 확인
            chunk_lower = chunk.lower()
            if any(keyword in chunk_lower for keyword in ["인공지능", "AI", "튜링", "머신러닝", "신경망", "딥러닝"]):
                relevant_chunks.append(chunk)
                if len(relevant_chunks) >= top_k:
                    break
        
        # 4. LLM에 질문 및 답변 생성 (일시적으로 비활성화)
        # context = "\n\n".join(relevant_chunks[:top_k])
        # prompt = f"""다음은 인공지능에 대한 정보입니다:
        # 
        # {context}
        # 
        # 질문: {question}
        # 
        # 위의 정보를 바탕으로 질문에 답변해주세요. 정보에 없는 내용은 추측하지 말고, 정보에 있는 내용만을 바탕으로 답변해주세요."""
        # 
        # response = client.chat.completions.create(
        #     model="gpt-3.5-turbo",
        #     messages=[
        #         {"role": "system", "content": "당신은 인공지능 전문가입니다. 주어진 정보를 바탕으로 정확하고 간결하게 답변해주세요."},
        #         {"role": "user", "content": prompt}
        #     ],
        #     temperature=temperature,
        #     max_tokens=500
        # )
        # 
        # gpt_answer = response.choices[0].message.content
        
        # 임시 답변
        gpt_answer = f"청킹 전략 {chunk_strategy}로 {len(chunks)}개 청크 생성, {len(relevant_chunks)}개 관련 청크 검색됨"
        
        # 5. 간단한 평가 메트릭 (실제로는 더 정교한 평가 필요)
        question_type = get_question_type(question)
        
        # 임시 평가 메트릭 (실제로는 정답과 비교해야 함)
        evaluation_f1 = 0.8 if len(relevant_chunks) > 0 else 0.0
        evaluation_recall = len(relevant_chunks) >= min(top_k, 3)
        
        result = {
            "chunk_strategy": chunk_strategy,
            "question_type": question_type,
            "question": question,
            "top_k": top_k,
            "temperature": temperature,
            "retrieved_chunks": str([chunk[:100] + "..." if len(chunk) > 100 else chunk for chunk in relevant_chunks]),
            "gpt_answer": gpt_answer,
            "evaluation_metric_F1": evaluation_f1,
            "evaluation_metric_Recall@5": evaluation_recall
        }
        return result
        
    except Exception as e:
        print(f"Error in experiment: {e}")
        return {
            "chunk_strategy": chunk_strategy,
            "question_type": "error",
            "question": question,
            "top_k": top_k,
            "temperature": temperature,
            "retrieved_chunks": "error",
            "gpt_answer": f"Error: {str(e)}",
            "evaluation_metric_F1": 0.0,
            "evaluation_metric_Recall@5": False
        }

# ─── 메인 실행 함수 ───────────────────────────────────────────────

def main():
    print("Grid search 실험을 시작합니다...")
    # os.makedirs(os.path.dirname(OUTPUT_CSV_PATH), exist_ok=True) # 이 줄은 이제 필요 없음

    # 모든 파라미터 조합 생성
    all_questions = list(itertools.chain.from_iterable(QUESTION_SAMPLES.values()))
    param_grid = list(itertools.product(
        CHUNK_STRATEGIES,
        all_questions,
        TOP_K_VALUES,
        TEMPERATURE_VALUES
    ))

    # CSV 파일 준비
    with open(OUTPUT_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["chunk_strategy", "question_type", "question", "top_k", "temperature", "retrieved_chunks", "gpt_answer", "evaluation_metric_F1", "evaluation_metric_Recall@5"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # 각 조합에 대해 실험 실행
        for i, params in enumerate(param_grid):
            strategy, question, k, temp = params
            print(f"Running experiment {i+1}/{len(param_grid)}: {params}")
            
            result = run_single_experiment(strategy, question, k, temp)
            writer.writerow(result)

    print(f"실험 완료. 결과가 다음 파일에 저장되었습니다: {OUTPUT_CSV_PATH}")

if __name__ == "__main__":
    main() 