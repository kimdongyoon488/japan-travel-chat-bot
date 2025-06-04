import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# 파일 경로
chunk_path = "data/fukuoka_guide_chunks.json"
index_path = "data/fukuoka_faiss.index"
metadata_path = "data/fukuoka_metadata.json"  # optional: chunk별 원문 저장

# chunk 로드
with open(chunk_path, "r", encoding="utf-8") as f:
    chunks = json.load(f)

print(f" {len(chunks)}개 chunk 불러옴")

# 임베딩
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(chunks, show_progress_bar=True)
embeddings = np.array(embeddings).astype("float32")  # FAISS용 변환

# FAISS 인덱스 생성 및 저장
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)  # L2 거리 기반 검색
index.add(embeddings)
faiss.write_index(index, index_path)
print(f"FAISS 인덱스 저장 완료 → {index_path}")


# metadata 저장 (나중에 검색 결과 → 원문 매핑용)
with open(metadata_path, "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)
print(f"metadata 저장 완료 → {metadata_path}")



