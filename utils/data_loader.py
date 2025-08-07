from pathlib import Path

TEXT_PATH  = "data/text_chunks.txt"

def load_chunks(path=TEXT_PATH):
    """
    지정된 경로의 텍스트 파일을 읽어,
    빈 줄 두 개를 기준으로 조각내어 리스트로 반환합니다.
    """
    with open(path, encoding="utf-8") as f:
        return [c.strip() for c in f.read().split("\n\n") if c.strip()] 