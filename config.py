# ─── 설정 변수 ───────────────────────────────────
# 이 파일에서 프로젝트 전체의 설정을 관리합니다.
# 모델 이름, 파일 경로 등 변경 가능성이 있는 값들을 여기서 한번에 관리하면 편리합니다.
# ───────────────────────────────────────────────────

# OpenAI 모델 설정
EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL  = "gpt-4-1106-preview" # RAG 답변 생성에 사용할 모델

# 데이터 및 인덱스 경로
INDEX_PATH = "data/index.faiss"       # Faiss 벡터 인덱스 파일 경로
TEXT_PATH  = "data/text_chunks.txt"  # 원본 텍스트 조각 파일 경로
LOG_DIR    = "logs"                  # 로그 파일 저장 디렉토리
CHAT_LOG_PATH = f"{LOG_DIR}/chat_logs.csv" # 대화 로그 파일 경로
RESULTS_CSV_PATH = "experiments/results/grid_search_latest.csv" # 최신 실험 결과 CSV 경로

# CORS 설정
# 여기에 허용할 프론트엔드 주소를 추가하세요.
# 예: ["http://localhost:3000", "https://your-frontend.com"]
ALLOWED_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://gpt-fastapi-app.onrender.com"
]

# S3 저장 설정
USE_S3 = True  # 무료 플랜에서 인스턴스 로컬 디스크 공유 불가 → S3 사용
S3_BUCKET = os.getenv("S3_BUCKET", "")
S3_REGION = os.getenv("S3_REGION", "ap-northeast-2")
S3_PREFIX = os.getenv("S3_PREFIX", "rag-sessions/")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN", "")
