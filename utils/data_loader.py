from pathlib import Path
import re

TEXT_PATH  = "data/text_chunks.txt"

def load_chunks(path=TEXT_PATH):
    """
    지정된 경로의 텍스트 파일을 읽어,
    두 줄 이상의 공백 줄을 기준으로 조각내어 리스트로 반환합니다.
    """
    with open(path, encoding="utf-8") as f:
        content = f.read()
    parts = re.split(r"\n{2,}", content)
    return [c.strip() for c in parts if c.strip()] 