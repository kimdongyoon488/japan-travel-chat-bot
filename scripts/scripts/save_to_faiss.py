import json
from sentence_transformers import SentenceTransformer
import numpy as np
import os
import faiss


INPUT_PATH = "data/raw/fukuoka_raw1.json"
EMBEDDING_OUTPUT = "data/fukuoka_embeddings.npy"
METADATA_OUTPUT = "data/fukuoka_metadata.json"
FAISS_OUTPUT = "data/fukuoka_faiss.index"

model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

texts = []
metas = []
#
# def handle_detail_page(item):
#     content = item.get("content", "").strip()
#     info_table = item.get("info_table", {})
#     info_text = "\n".join(f"{k}: {v}" for k, v in info_table.items())
#     if content or info_text:
#         return [((content + ("\n" + info_text if info_text else "")).strip(), item["url"])]
#     return []
#
# def handle_section_detail(item):
#     content = item.get("content", "").strip()
#     if content:
#         return [(content, item["url"])]
#     return []
#
# def handle_course_page(item):
#     out = []
#     for spot in item.get("spots", []):
#         desc = spot.get("description", "").strip()
#         if desc:
#             out.append((desc, item["url"]))
#     return out

def handle_detail_page(item):
    chunks = []
    url = item.get("url", "")
    title = item.get("title", "")

    content = item.get("content", "").strip()
    if content:
        chunks.append((content, url, title))

    info_table = item.get("info_table", {})
    for k, v in info_table.items():
        if isinstance(v, list):
            for v_item in v:
                v_item = v_item.strip()
                if v_item:
                    chunks.append((f"{k}: {v_item}", url, title))
        else:
            v = str(v).strip()
            if v:
                chunks.append((f"{k}: {v}", url, title))
    return chunks

def handle_section_detail(item):
    chunks = []
    url = item.get("url", "")
    title = item.get("title", "")
    content = item.get("content", "").strip()
    if content:
        chunks.append((content, url, title))
    info_table = item.get("info_table", {})
    for k, v in info_table.items():
        if isinstance(v, list):
            for v_item in v:
                v_item = v_item.strip()
                if v_item:
                    chunks.append((f"{k}: {v_item}", url, title))
        else:
            v = str(v).strip()
            if v:
                chunks.append((f"{k}: {v}", url, title))
    return chunks

def handle_course_page(item):
    chunks = []
    url = item.get("url", "")
    title = item.get("title", "")
    description = item.get("description", "").strip()
    if description:
        chunks.append((description, url, title))
    for spot in item.get("spots", []):
        spot_section = spot.get("section", "").strip()
        spot_desc = spot.get("description", "").strip()
        # spot section+desc 각각 chunk화
        if spot_section:
            chunks.append((spot_section, url, title))
        if spot_desc:
            chunks.append((spot_desc, url, title))
        info_table = spot.get("info_table", {})
        for k, v in info_table.items():
            if isinstance(v, list):
                for v_item in v:
                    v_item = v_item.strip()
                    if v_item:
                        chunks.append((f"{k}: {v_item}", url, title))
            else:
                v = str(v).strip()
                if v:
                    chunks.append((f"{k}: {v}", url, title))
    return chunks

for entry in raw_data:
    entry_type = entry.get("type")
    if entry_type == "detail_page":
        chunks = handle_detail_page(entry)
    elif entry_type == "section_detail":
        chunks = handle_section_detail(entry)
    elif entry_type in ["itinerary_course", "course_page"]:
        chunks = handle_course_page(entry)
    else:
        chunks = []

    for text, url, title in chunks:
        texts.append(text)
        metas.append({"url": url, "title": title, "text": text})

# 임베딩 수행
embeddings = model.encode(texts, show_progress_bar=True)
np.save(EMBEDDING_OUTPUT, embeddings)

# FAISS 인덱스 생성 및 저장
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)        # L2 거리 기반 단순 인덱스
index.add(embeddings.astype(np.float32))    # FAISS는 float32만 허용
faiss.write_index(index, FAISS_OUTPUT)      # 인덱스 저장

# 메타데이터 저장
with open(METADATA_OUTPUT, "w", encoding="utf-8") as f:
    json.dump(metas, f, ensure_ascii=False, indent=2)

print(f"[DONE] {len(texts)} 임베딩 후 FAISS 저장 완료.")