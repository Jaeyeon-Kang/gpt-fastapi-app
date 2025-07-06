# generate_embedding.py
import os, faiss, numpy as np
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from utils.data_loader import load_chunks

# ── 설정 ──────────────────────────────────────────
INDEX_PATH  = "data/index.faiss"
EMBED_MODEL = "text-embedding-3-small"
# ─────────────────────────────────────────────────

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def build_index(chunks):
    if not chunks:
        print("🤷‍♀️ 인덱스를 만들 텍스트 조각이 없습니다. data/text_chunks.txt 파일이 비어있는지 확인해보세요.")
        # 비어있는 index.faiss 파일을 만들거나 그냥 리턴할 수 있습니다.
        # 여기서는 그냥 리턴하여 아무 작업도 하지 않도록 합니다.
        return

    embeds = []
    for i, chunk in enumerate(chunks, 1):
        print(f"🔹 [{i}/{len(chunks)}] embedding: {chunk[:30]}…")
        emb = client.embeddings.create(input=chunk, model=EMBED_MODEL).data[0].embedding
        embeds.append(emb)

    xb   = np.array(embeds, dtype="float32")
    dim  = xb.shape[1]
    idx  = faiss.IndexFlatL2(dim)
    idx.add(xb)  # type: ignore
    Path(INDEX_PATH).parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(idx, INDEX_PATH)
    print(f"✅ wrote {len(chunks)} vectors → {INDEX_PATH}")

if __name__ == "__main__":
    chunks_to_build = load_chunks()
    build_index(chunks_to_build)