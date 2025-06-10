from googletrans import Translator
import os

input_path = "data/fukuoka_guide_ocr.txt"
output_path = "data/fukuoka_guide_ocr_en.txt"

translator = Translator()

with open(input_path, "r", encoding="utf-8") as f:
    korean_text = f.read()

# 문장 단위로 자르기 (줄 단위 처리)
lines = korean_text.strip().split("\n")
translated_lines = []

for line in lines:
    line = line.strip()
    if not line:
        continue

    try:
        result = translator.translate(line, src="ko", dest="en")
        translated_lines.append(result.text)
    except Exception as e:
        print(f"[번역 실패] {line} → {e}")
        continue

# 번역 결과 저장
with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(translated_lines))

print(f"번역 완료 → 저장 위치: {output_path}")