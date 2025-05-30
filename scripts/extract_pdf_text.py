from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import os

pdf_path = "data/fukuoka_guide.pdf"
output_path = "data/fukuoka_guide_ocr.txt"

# 윈도우: Tesseract 경로
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

pages = convert_from_path(pdf_path, dpi=400)
text = ""

for page in pages:
    temp_img_path = "temp_page.jpg"
    page.save(temp_img_path, "JPEG")
    text += pytesseract.image_to_string(Image.open(temp_img_path), lang="eng+kor") + "\n\n"
    os.remove(temp_img_path)

with open(output_path, "w", encoding="utf-8") as f:
    f.write(text)

print("OCR 텍스트 추출 완료: data/fukuoka_guide_ocr.txt")
