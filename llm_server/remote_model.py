import requests

COLAB_API_URL = "https://64ec-34-124-200-225.ngrok-free.app/generate/"

def generate_with_remote_model(prompt: str) -> str:
    try:
        response = requests.post(COLAB_API_URL, json={"prompt": prompt})
        response.raise_for_status()
        return response.json().get("answer", "")
    except Exception as e:
        print(f"[ERROR] Colab 서버 요청 실패: {e}")
        return "죄송합니다. 현재 모델 응답에 문제가 발생했습니다."
