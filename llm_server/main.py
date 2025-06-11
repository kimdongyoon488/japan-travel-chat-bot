from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from llm_server.rag_pipeline import get_answer

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "FAST API 정상 동작"}

@app.get("/ask")
def ask(question: str = Query(..., description="사용자 질문")):
    try:
        print("get_answer 함수 호출됨")
        answer = get_answer(question)
        return {"question": question, "answer": answer}
    except Exception as e:
        print(f"get_answer 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
