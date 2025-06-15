import json
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer
# from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from llm_server.config import FAISS_INDEX_PATH, METADATA_PATH
#from transformers import GPT2Tokenizer
from llm_server.remote_model import generate_with_remote_model


# 모델/인덱스 로드 (최초 1회)
embedder  = SentenceTransformer("jhgan/ko-sroberta-multitask")
index = faiss.read_index(FAISS_INDEX_PATH)

with open(METADATA_PATH, "r", encoding="utf-8") as f:
    chunks = json.load(f)

# LLM 생성기(Hugging Face summarizer)
# llm = pipeline("text2text-generation", model="google/flan-t5-small")
# tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

# pipeline 대신 tokenizer + model 직접 사용
# llm = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
# tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")

#모델 변경 (flan-t5-small → flan-t5-base)
# llm = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")
# tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")





def get_answer(query: str):

    # 쿼리 임베딩
    query_vec = embedder.encode([query]).astype("float32")

    top_k = 2
    _, indices = index.search(query_vec, top_k)

    beer_chunk = chunks[386]["text"]
    beer_vec = embedder.encode([beer_chunk])[0]

    cos_sim = np.dot(query_vec, beer_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(beer_vec))
    print("쿼리와 beer_chunk의 코사인 유사도:", cos_sim)


    print("indices[0]:", indices[0])
    for i in indices[0]:
        if i < len(chunks):
            print("==> 검색 결과 chunk[{}]".format(i))
            print("  title:", chunks[i].get("title"))
            print("  text :", chunks[i].get("text"))
            print("  url  :", chunks[i].get("url"))


    # print("chunks type:", type(chunks))
    # print("예시 chunks[0]:", chunks[0] if hasattr(chunks, '__getitem__') else None)
    # print("indices[0]:", indices[0])

    retrieved_chunks = []

    for i in indices[0]:
        if i < len(chunks):
            # 각 chunk는 dict이므로 'text' 필드만 슬라이싱
            text = chunks[i].get("text", "")
            retrieved_chunks.append(text[:300])
        else:
            print(f"경고: 인덱스 {i}가 chunks 길이 {len(chunks)}를 벗어남")
    context = "\n".join(retrieved_chunks)

    if len(context) > 1000:
        context = context[:1000]

    prompt = (
        f"다음은 사용자의 질문에 친절하게 답변하는 한국어 인공지능 비서입니다.\n\n"
        f"[문서]\n{context}\n\n[질문]\n{query}\n\n[답변]"
    )

    print("=== START context ===")
    print(context)
    print("=== END context ===")

    print("=== START prompt ===")
    print(prompt)
    print("=== END prompt ===")

    # Colab 서버에 프롬프트 전송
    answer = generate_with_remote_model(prompt)
    print("=== Start answer ===")
    print(repr(answer))
    print("=== End answer ===")

    # return answer.split("답변:")[-1].strip()
    #return answer.strip()

    return answer

