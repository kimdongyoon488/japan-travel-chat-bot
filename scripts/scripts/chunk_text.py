import os
import re
import json

# 경로 설정
input_path = "data/fukuoka_guide_ocr.txt"
output_path = "data/fukuoka_guide_chunks.json"

# 파라미터 설정
chunk_size = 500       
chunk_overlap = 100    

# 텍스트 불러오기
with open(input_path, "r", encoding="utf-8") as f:
    raw_text = f.read()

# 줄바꿈/공백 정리
cleaned_text = re.sub(r"\s+", " ", raw_text).strip()

# 슬라이딩 윈도우 방식으로 chunk 자르기
chunks = []
text_length = len(cleaned_text)

for i in range(0, text_length, chunk_size - chunk_overlap):
    chunk = cleaned_text[i:i+chunk_size].strip()
    if len(chunk) > 100:  # 너무 짧은 건 제외
        chunks.append(chunk)

# JSON 저장
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)

print(f"총 {len(chunks)}개의 chunk 저장 완료 → {output_path}")