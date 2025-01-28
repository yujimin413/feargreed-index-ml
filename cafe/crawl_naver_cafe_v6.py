# 
# 키워드별 수집, content 수집 됨 
# 페이징 기능 추가함
# 10 페이지 이상 "다음" 버튼 반영 페이징 성공

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException

from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")  # 리눅스 환경에서 유용
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-extensions")
options.add_argument("--disable-logging")

# driver = webdriver.Chrome(options=options)


import time
import pyperclip
import os
import csv
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

NAVER_ID = os.getenv("NAVER_ID")
NAVER_PW = os.getenv("NAVER_PW")

# Keywords
# keywords = [
#     "부동산 호황", "매수 타이밍", "재건축 기대", "저금리 효과",
#     "개발 호재", "시장 회복", "신규 분양 열기", "자산 가치 상승", "투자 기회",
#     "강남 아파트 상승", "임대 수익"
# ]
keywords = [
    "집값 폭락", "부동산 거품", "금리 인상", "대출 규제", "거래 절벽",
    "전세난", "주택 매매 침체", "부동산 하락", "경제 위기", "디폴트 위기",
    "경기 침체", "대출 상환 부담", "경매 급증", "시장 불안", "매물 증가",
    "재산세 부담", "공급 과잉"
]

# Function to log in to Naver
def naver_login(driver, naver_id, naver_pw):
    driver.get("https://nid.naver.com/nidlogin.login")
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "id")))
        time.sleep(1)

        # Enter ID
        id_input = driver.find_element(By.ID, "id")
        pyperclip.copy(naver_id)
        id_input.click()
        id_input.send_keys(Keys.COMMAND + 'v')

        # Enter password
        password_input = driver.find_element(By.ID, "pw")
        pyperclip.copy(naver_pw)
        time.sleep(1)
        password_input.click()
        password_input.send_keys(Keys.COMMAND + 'v')

        # Click login button
        sign_in_button = driver.find_element(By.ID, "log.login")
        sign_in_button.click()
        time.sleep(1)
    except TimeoutException:
        print("Login timed out.")
        driver.quit()

def crawl_cafe(driver, keywords, start_date, end_date, output_file):
    driver.get("https://cafe.naver.com/jaegebal")
    time.sleep(1)

    driver.switch_to.default_content()
    print("[DEBUG] Returned to main content")
    search_bar = driver.find_element(By.ID, "topLayerQueryInput")
    search_bar.click()
    search_bar.clear()
    search_bar.send_keys("dummy")
    search_bar.send_keys(Keys.RETURN)
    time.sleep(1)

    data = []
    for keyword in keywords:  # keywords 리스트 내 검색어 순회
        try:
            print(f"Searching for keyword: {keyword}")
            driver.switch_to.frame("cafe_main")
            print("[DEBUG] Switched to iframe")
            
            # "제목만" 클릭
            select_box = driver.find_element(By.ID, "currentSearchByTop")
            select_box.click()
            title_option = driver.find_element(By.XPATH, "//a[text()='제목만']")
            title_option.click()

            # 검색어 입력
            search_input = driver.find_element(By.ID, "queryTop")
            search_input.clear()
            search_input.send_keys(keyword)
            search_input.send_keys(Keys.RETURN)
            time.sleep(1)

            page_number = 1  # 페이지 번호 추적
            while True:  # 페이지 그룹 순회
                page_buttons = driver.find_elements(By.CSS_SELECTOR, ".prev-next a:not(.pgR)")  # 현재 페이지 버튼들
                for button in page_buttons:
                    # 현재 페이지 번호에 해당하는 버튼 클릭
                    button_text = button.text.strip()
                    if button_text.isdigit() and int(button_text) == page_number:
                        print(f"[DEBUG] Clicking page {page_number} for keyword: {keyword}")
                        button.click()
                        time.sleep(1)
                        break

                rows = driver.find_elements(By.CSS_SELECTOR, "#main-area > div:nth-child(5) > table > tbody > tr")
                print(f"[DEBUG] Found {len(rows)} rows on page {page_number}")

                for row_index in range(len(rows)):
                    try:
                        print(f"[DEBUG] Processing row {row_index + 1}")

                        rows = driver.find_elements(By.CSS_SELECTOR, "#main-area > div:nth-child(5) > table > tbody > tr")  # 모든 행 선택  
                        row = rows[row_index]
                        
                        title_element = row.find_element(By.CSS_SELECTOR, "td.td_article .article")
                        title = title_element.text
                        print(f"[DEBUG] Title: {title}")
                        link = title_element.get_attribute("href")
                        author = row.find_element(By.CSS_SELECTOR, "td.td_name .m-tcol-c").text
                        date = row.find_element(By.CSS_SELECTOR, "td.td_date").text
                        if date < start_date or date > end_date:
                            continue
                        views = row.find_element(By.CSS_SELECTOR, "td.td_view").text

                        # 게시글 클릭 및 내용 수집
                        title_element.click()
                        time.sleep(1)

                        driver.switch_to.default_content()
                        driver.switch_to.frame("cafe_main")
                        
                        try:
                            content_element = driver.find_element(By.CLASS_NAME, "se-main-container")
                            content = content_element.text
                        except NoSuchElementException:
                            try:
                                content_element = driver.find_element(By.CLASS_NAME, "txt")
                                content = content_element.text
                            except NoSuchElementException:
                                try:
                                    content_element = driver.find_element(By.CLASS_NAME, "scrap_added")
                                    content = content_element.text
                                except NoSuchElementException:
                                    try:
                                        content_element = driver.find_element(By.CLASS_NAME, "se-component-content")
                                        content = content_element.text
                                    except NoSuchElementException:
                                        content = "Content not found"

                        driver.back()
                        time.sleep(1)
                        driver.switch_to.frame("cafe_main")
                        data.append([keyword, date, title, content, link, author, views])

                    except Exception as e:
                        print(f"[DEBUG] Error processing row {row_index + 1}: {e}")

                page_number += 1  # 페이지 번호 증가

                # 다음 페이지 그룹으로 이동
                if page_number % 10 == 1:
                    print(f"[DEBUG] Moving to next page group after page {page_number - 1}")
                    try:
                        next_button = driver.find_element(By.CSS_SELECTOR, ".prev-next a.pgR")
                        next_button.click()
                        time.sleep(2)  # 페이지 그룹 로드 대기
                    except NoSuchElementException:
                        print(f"No more pages for keyword: {keyword}")
                        break  # 다음 키워드로 이동
                else:
                    # 현재 페이지에서 다음 페이지를 클릭하도록 루프 유지
                    continue

        except NoSuchElementException as e:
            print(f"Error switching to iframe or finding rows: {e}")

        driver.switch_to.default_content()

    # Save to CSV
    with open(output_file, mode="w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Keyword", "Date", "Title", "Content", "Link", "Author", "Views"])
        writer.writerows(data)
    print(f"Data saved to {output_file}")


    # Save to CSV
    with open(output_file, mode="w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Keyword", "Date", "Title", "Content", "Link", "Author", "Views"])
        writer.writerows(data)
    print(f"Data saved to {output_file}")


    

# Main script
if __name__ == "__main__":
    # User-defined parameters
    start_date = input("Enter start date (YYYY.MM.DD): ")
    end_date = input("Enter end date (YYYY.MM.DD): ")

    timestamp = datetime.now().strftime("%y%m%d_%H%M")
    # output_file = "cafe_data.csv"
    output_file = f"cafe_data_공포{timestamp}.csv"

    # Initialize WebDriver
    # driver = webdriver.Chrome()  # Ensure chromedriver is in your PATH
    driver = webdriver.Chrome(options=options)

    try:
        naver_login(driver, NAVER_ID, NAVER_PW)
        # crawl_cafe(driver, keywords, start_date, end_date, output_file)
        

        try:
            # 웹 크롤링 수행
            crawl_cafe(driver, keywords, start_date, end_date, output_file)
        except WebDriverException as e:
            print(f"[ERROR] WebDriverException occurred: {e}")
            print("[INFO] Restarting the browser...")
            driver.qui