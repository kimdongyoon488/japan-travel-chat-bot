import json
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

INPUT_PATH = "data/raw/fukuoka_raw1.json"
EMBEDDING_OUTPUT = "data/fukuoka_embeddings.npy"
METADATA_OUTPUT = "data/fukuoka_metadata.json"
FAISS_OUTPUT = "data/fukuoka_faiss.index"

model = SentenceTransformer("jhgan/ko-sroberta-multitask")

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

texts = []
metas = []

def handle_detail_page(item):
    url = item.get("url", "")
    title = item.get("title", "")
    content = item.get("content", "").strip()
    info_table = item.get("info_table", {})

    info_lines = []
    info = {}
    for key, value in info_table.items():
        if isinstance(value, list):
            value_str = "\n".join(v.strip() for v in value)
            info[key] = value_str
        else:
            info[key] = value
        info_lines.append(f"{key}: {info[key]}")

    full_text = f"{title}\n{content}\n" + "\n".join(info_lines)

    return [(url, title, full_text, info)]


def handle_section_detail(item):
    url = item.get("url", "")
    title = item.get("title", "")
    spots = item.get("spots", [])

    chunks = []
    for spot in spots:
        section = spot.get("section", "").strip()
        desc = spot.get("description", "").strip()
        full_text = f"{section}\n{desc}"
        chunks.append((url, title, full_text, {}))

    return chunks


def handle_course_page(item):
    url = item.get("url", "")
    title = item.get("title", "")
    description = item.get("description", "").strip()
    spots = item.get("spots", [])

    chunks = []
    if description:
        chunks.append((url, title, description, {}))

    for spot in spots:
        section = spot.get("section", "").strip()
        desc = spot.get("description", "").strip()
        info_table = spot.get("info_table", {})

        info_lines = []
        info = {}
        for key, value in info_table.items():
            if isinstance(value, list):
                value_str = "\n".join(v.strip() for v in value)
                info[key] = value_str
            else:
                info[key] = value
            info_lines.append(f"{key}: {info[key]}")

        full_text = f"{section}\n{desc}\n" + "\n".join(info_lines)
        chunks.append((url, title, full_text, info))

    return chunks


for entry in raw_data:
    entry_type = entry.get("type")

    if entry_type == "detail_page":
        chunks = handle_detail_page(entry)
    elif entry_type == "section_detail":
        chunks = handle_section_detail(entry)
    elif entry_type == "course_page":
        chunks = handle_course_page(entry)
    else:
        chunks = []

    for url, title, text, info in chunks:
        texts.append(text)
        metas.append({"url": url, "title": title, "text": text, "info": info})


# 임베딩 수행
embeddings = model.encode(texts, show_progress_bar=True)
np.save(EMBEDDING_OUTPUT, embeddings)

# FAISS 인덱스 생성 및 저장
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings.astype(np.float32))
faiss.write_index(index, FAISS_OUTPUT)

# 메타데이터 저장
with open(METADATA_OUTPUT, "w", encoding="utf-8") as f:
    json.dump(metas, f, ensure_ascii=False, indent=2)

print(f"[DONE] {len(texts)}개 chunk 임베딩 후 FAISS 저장 완료.")
