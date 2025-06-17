from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from llm_server.rag_pipeline import get_answer
app = FastAPI()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 단계에선 * 로 허용, 배포 시엔 실제 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
