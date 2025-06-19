import json
import faiss
import numpy as np
import hashlib
import re
import unicodedata


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
    seen_norm_texts = set()


    #중복 chunk 제거
    for i in indices[0]:
        if i < len(chunks):
            raw_text = chunks[i].get("text", "")
            normalized = normalize_text(raw_text)
            h = hashlib.md5(normalized.encode("utf-8")).hexdigest()

            if normalized not in seen_norm_texts:
                retrieved_chunks.append(raw_text)
                seen_norm_texts.add(normalized)  # 정규화된 텍스트로 비교
            else:
                print(f"중복 제거된 chunk index: {i}")


    context = "\n".join(retrieved_chunks)

    if len(context) > 1500:
        context = context[:1500]

    # prompt = (
    #     f"다음은 사용자의 질문에 친절하게 답변하는 한국어 인공지능 비서입니다.\n\n"
    #     f"[문서]\n{context}\n\n[질문]\n{query}\n\n[답변]"
    # )
    #
    # prompt = f"""
    # 너는 여행 정보를 잘 아는 한국어 비서야.
    # 사용자의 질문에 문서를 참고해서 친절하게 알려줘.
    #
    # 문서:
    # {context}
    #
    # 질문: {query}
    # """

    if context.strip():
        prompt = f"""
        너는 한국어로 여행 정보를 알려주는 친절한 AI야.
        답변을 여러번 하지 말고 문서를 참고해서 질문에 대해 딱 한 번, 정중하게 답해줘.

        문서 정보:
        {context}

        질문: {query}
        답변:"""

    # if context.strip():
    #     prompt = f"""
    #     아래 문서를 참고하여 사용자의 질문에 관련된 것만 친절하게 존댓말로 답변해줘.
    #
    #     문서 정보:
    #     {context}
    #
    #     질문: {query}
    #     답변:"""

    else:
        prompt = f"""
        사용자의 질문에 존댓말로 한 번만 답변해줘.

        질문: {query}
        답변:"""


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

    raw_text_1 = chunks[36]["text"]
    raw_text_2 = chunks[994]["text"]

    print("== 차이 여부 ==")
    print("동일?", raw_text_1 == raw_text_2)

    norm1 = normalize_text(raw_text_1)
    norm2 = normalize_text(raw_text_2)

    print("== 정규화 후 비교 ==")
    print("정규화 후 동일?", norm1 == norm2)

    print("정규화 후 1:", repr(norm1))
    print("정규화 후 2:", repr(norm2))

    print("정규화 후 1:", [ord(c) for c in norm1])
    print("정규화 후 2:", [ord(c) for c in norm2])

    return answer


# chunk 비교 시 정규화 하여 비교 진행
def normalize_text(text: str) -> str:
    # 유니코드 정규화 (전각/반각, 특수문자 등 통일)
    text = unicodedata.normalize("NFKC", text).strip()

    # 줄바꿈/탭/전각공백 제거 → 일반 공백으로 통일
    text = text.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    text = text.replace("\u3000", " ")  # ← 전각 공백 (full-width space) 제거

    # 다중 공백 압축
    text = re.sub(r"\s+", " ", text)

    return text.strip()