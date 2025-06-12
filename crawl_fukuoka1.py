import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import json

BASE_URL = "https://www.crossroadfukuoka.jp/kr"
OUTPUT_PATH = "data/raw/fukuoka_raw1.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# 일반적인 리스트 페이지들 (하위 페이지를 따로 가지는 구조)
NAV_LINKS = [
    "https://www.crossroadfukuoka.jp/kr/spot",         # 관광지
    "https://www.crossroadfukuoka.jp/kr/articles",     # 특집 기사 목록
    "https://www.crossroadfukuoka.jp/kr/itineraries",  # 추천 코스
    "https://www.crossroadfukuoka.jp/kr/experience",   # 체험
    "https://www.crossroadfukuoka.jp/kr/event"         # 이벤트
]

def get_detail_links(list_url):
    res = requests.get(list_url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        full_url = urljoin(BASE_URL, href)
        # 상세 페이지는 /kr/카테고리/xxx 형식이며, 숫자든 문자열이든 가능
        if full_url.startswith(list_url) and len(full_url.split("/")) > 5:
            links.append(full_url)

    return list(set(links))

def extract_page_content(url):
    try:
        res = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")

        # 제목
        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else ""

        # content
        desc_tag = soup.find("h2", class_="o-detail-contents__description")
        content = desc_tag.get_text(separator="\n", strip=True) if desc_tag else ""

        # info_table
        info_table = {}
        info_table_tag = soup.find("table", class_="o-detail-contents__table")
        if info_table_tag:
            for row in info_table_tag.find_all("tr"):
                th = row.find("th")
                td = row.find("td")
                if th and td:
                    key = th.get_text(strip=True)
                    if td.find_all("a"):
                        value = [a.get("href") for a in td.find_all("a") if a.get("href")]
                    else:
                        value = td.get_text(separator="\n", strip=True)
                    info_table[key] = value


        return {
            "url": url,
            "title": title,
            "content": content,
            "info_table": info_table
        }
    except Exception as e:
        print(f"[ERROR] {url}: {e}")
        return None

# 섹션 페이지 추출
def extract_sections_from_plan_page(url):
    print(f"[INFO] Extracting sections from: {url}")
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    sections = soup.find_all("div", id=lambda x: x and x.startswith("section-"))
    data_list = []

    for section in sections:
        section_id = section.get("id")
        title = section.find(["h1", "h2", "h3"])
        content = section.get_text(separator="\n", strip=True)

        if content:
            data_list.append({
                "url": f"{url}#{section_id}",
                "title": title.get_text(strip=True) if title else f"Section {section_id}",
                "content": content
            })

    print(f"  └─ {len(data_list)} sections extracted")
    return data_list


#추천 코스 페이지 추출
def extract_itinerary_page_content(url):
    try:
        res = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")

        # HTML <title> 태그로 제목 덮어쓰기
        html_title = soup.title.string.strip() if soup.title else ""

        # <meta name="description"> 값 추출
        meta_tag = soup.find("meta", attrs={"name": "description"})
        description = meta_tag["content"].strip() if meta_tag and "content" in meta_tag.attrs else ""

        # 각 코스 구간
        spots = []
        spot_boxes = soup.find_all("div", class_="o-model-course-spot__box")

        for spot_box in spot_boxes:
            spot = {}

            h4 = spot_box.find_previous("h4")
            if h4:
                spot["section"] = h4.get_text(strip=True)

            spot_title = spot_box.find("h5", class_="o-model-course-spot__title")
            if spot_title:
                spot["title"] = spot_title.get_text(strip=True)

            # body = spot_box.get_text(separator="\n", strip=True)
            # spot["body"] = body

            # 코스별 설명 추출
            right_box = spot_box.find("div", class_="o-model-course-spot__box-inner--right")
            if right_box:
                desc_tag = right_box.find("div", class_="o-detail-contents__description")
                if desc_tag:
                    spot["description"] = desc_tag.get_text(separator="\n", strip=True)


            #코스별 기본정보 추출
            info_table = {}
            table = spot_box.find("table", class_=lambda c: c and "o-detail-contents__table" in c)
            if table:
                for row in table.find_all("tr"):
                    th = row.find("th")
                    td = row.find("td")
                    if th and td:
                        key = th.get_text(strip=True)
                        if td.find_all("a"):
                            value = [a.get("href") for a in td.find_all("a") if a.get("href")]
                        else:
                            value = td.get_text(separator="\n", strip=True)
                        info_table[key] = value
                if info_table:  # ✅ 비어있지 않으면만 추가
                    spot["info_table"] = info_table


            spots.append(spot)

        return {
            "url": url,
            "type": "itinerary_course",
            "title": html_title,
            "description": description,
            "spots": spots
        }
    except Exception as e:
        print(f"[ERROR] {url}: {e}")
        return None



def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    all_data = []

    # 1) NAV_LINKS 처리: detail 링크마다 섹션 페이지 / 일반 페이지 구분
    print(f"[INFO] Processing standard category pages...")
    for category_url in NAV_LINKS:
        print(f"[INFO] Scraping list: {category_url}")
        detail_urls = get_detail_links(category_url)
        print(f"  └─ {len(detail_urls)} detail pages found")

        for detail_url in detail_urls:

            # 추천 코스(코스형) 페이지: 별도 처리
            if "/itineraries/" in detail_url:
                print(f"[INFO] Itinerary course page: {detail_url}")
                item = extract_itinerary_page_content(detail_url)

                print("spots")
                print(item.get("spots"))
                if item and item.get("spots"):  # spot이 한 개라도 있으면 저장
                    all_data.append(item)
                else:
                    print(f"[SKIP] 본문 없음(추천코스): {detail_url}")
                continue

            # HTML 파싱
            res = requests.get(detail_url, headers=HEADERS)
            soup = BeautifulSoup(res.text, "html.parser")

            # 섹션 페이지 감지: id="section-XXX" 이 있는지
            sections = soup.find_all("div", id=lambda x: x and x.startswith("section-"))
            if sections:
                # 섹션별로 분리 추출
                print(f"[INFO] Section page detected: {detail_url}")
                section_data = extract_sections_from_plan_page(detail_url)
                all_data.extend(section_data)

            else:
                # 일반 상세 페이지
                item = extract_page_content(detail_url)
                if item and item["content"].strip():
                    all_data.append(item)
                else:
                    print(f"[SKIP] 본문 없음: {detail_url}")


    # 저장
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"[DONE] Saved {len(all_data)} pages to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()