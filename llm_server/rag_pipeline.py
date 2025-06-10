import json
import faiss

from sentence_transformers import SentenceTransformer
# from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from llm_server.config import FAISS_INDEX_PATH, METADATA_PATH
#from transformers import GPT2Tokenizer
from llm_server.remote_model import generate_with_remote_model


# 모델/인덱스 로드 (최초 1회)
embedder  = SentenceTransformer("all-MiniLM-L6-v2")
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
llm = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")
tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")





def get_answer(query: str):
    # 쿼리 임베딩
    query_vec = embedder.encode([query]).astype("float32")


    # FAISS 검색
    # top_k = 3
    # _, indices = index.search(query_vec, top_k)
    #
    # retrieved_chunks = [chunks[i] for i in indices[0]]
    # context = "\n".join(retrieved_chunks)

    top_k = 2
    _, indices = index.search(query_vec, top_k)
    retrieved_chunks = [chunks[i][:300] for i in indices[0]]
    context = "\n".join(retrieved_chunks)

    if len(context) > 1000:
        context = context[:1000]

    # LLM에 전달할 프롬프트
    # prompt = f"다음 정보를 참고해서 질문에 답해줘:\n\n{context}\n\n질문: {query}\n답변:"
    # prompt = f"다음 내용을 참고하여 질문에 대답해 주세요:\n\n{context}\n\n질문: {query}\n답:"

    # prompt = f"""질문에 대한 답변을 다음 문서를 참고해서 한국어로 간단하게 작성하세요.
    #
    # 문서:
    # {context}
    #
    # 질문: {query}
    # 답변:"""

    prompt = f"아래 내용을 참고하여 질문에 답해 주세요.\n\n[문서]\n{context}\n\n[질문]\n{query}\n\n[답변]"
    # prompt = "Question: What is the capital of Japan?\nAnswer:"


    #프롬프트 자르기
    # inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)

    # 응답 생성
    # output = llm.tokenizer.decode(
    #     llm.model.generate(**inputs, max_new_tokens=20, do_sample=True)[0],
    #     skip_special_tokens=True
    # )

    print("=== START context ===")
    print(context)
    print("=== END context ===")

    print("=== START prompt ===")
    print(prompt)
    print("=== END prompt ===")



    # 토크나이즈 (자동 잘림 포함)
    # inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)

    # 모델 생성
    # output = llm(prompt, max_new_tokens=200)[0]["generated_text"]
    # outputs = llm.generate(**inputs, max_new_tokens=150)
    # outputs = llm.generate(
    #     **inputs,
    #     max_new_tokens=150,
    #     do_sample=True,
    #     temperature=0.7,
    # )

    # outputs = llm.generate(
    #     **inputs,
    #     max_new_tokens=128,
    #     do_sample=True,
    #     temperature=0.9,
    #     top_p=0.95,
    #     repetition_penalty=1.1
    # )

    # outputs = llm.generate(**inputs, max_new_tokens=50)

    # print("=== START raw output ===")
    # # print(outputs)
    # print("=== END raw output ===")

    # answer = output.split("답변:")[-1].strip()
    # return answer

    # answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Colab 서버에 프롬프트 전송
    answer = generate_with_remote_model(prompt)
    print("=== Start answer ===")
    print(repr(answer))
    print("=== End answer ===")

    # return answer.split("답변:")[-1].strip()
    #return answer.strip()

    return answer

