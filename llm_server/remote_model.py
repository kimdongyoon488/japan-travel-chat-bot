import requests

COLAB_API_URL = "https://32da-34-143-217-31.ngrok-free.app/generate"

def generate_with_remote_model(prompt: str) -> str:
    try:
        response = requests.post(COLAB_API_URL, json={"prompt": prompt}, verify=False)
        response.raise_for_status()
        return response.json().get("answer", "")
    except Exception as e:
        print(f"[ERROR] Colab 서버 요청 실패: {e}")
        return "죄송합니다. 현재 모델 응답에 문제가 발생했습니다."
