# generate_embedding.py
import os, faiss, numpy as np
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# ── 설정 ──────────────────────────────────────────
TEXT_PATH   = "data/text_chunks.txt"
INDEX_PATH  = "data/index.faiss"
EMBED_MODEL = "text-embedding-3-small"
# ─────────────────────────────────────────────────

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_chunks(path=TEXT_PATH):
    with open(path, encoding="utf-8") as f:
        return [c.strip() for c in f.read().split("\n\n") if c.strip()]

def build_index(chunks):
    embeds = []
    for i, chunk in enumerate(chunks, 1):
        print(f"🔹 [{i}/{len(chunks)}] embedding: {chunk[:30]}…")
        emb = client.embeddings.create(input=chunk, model=EMBED_MODEL).data[0].embedding
        embeds.append(emb)

    xb   = np.array(embeds, dtype="float32")
    dim  = xb.shape[1]
    idx  = faiss.IndexFlatL2(dim)
    idx.add(xb)
    Path(INDEX_PATH).parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(idx, INDEX_PATH)
    print(f"✅ wrote {len(chunks)} vectors → {INDEX_PATH}")

if __name__ == "__main__":
    build_index(load_chunks())