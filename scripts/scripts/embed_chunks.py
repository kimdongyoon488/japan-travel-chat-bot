import json
from sentence_transformers import SentenceTransformer


chunk_path = "data/fukuoka_guide_chunks.json"

with open(chunk_path, "r", encoding="utf-8") as f:
    chunks = json.load(f)

print(f"{len(chunks)}개의 chunk 불러오기 완료")

model = SentenceTransformer("all-MiniLM-L6-v2")

# 임베딩
embeddings = model.encode(chunks, show_progress_bar=True)

print(f"임베딩 완료 → shape: {embeddings.shape}")