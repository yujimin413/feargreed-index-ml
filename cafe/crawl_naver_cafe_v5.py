# cafe_data_250127_2052.csv
# 키워드별 수집, content 수집 됨 (페이지 넘어가지 않음)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

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
keywords = [
    "집값 상승", "부동산 호황", "매수 타이밍", "재건축 기대", "저금리 효과",
    "개발 호재", "시장 회복", "신규 분양 열기", "자산 가치 상승", "투자 기회",
    "강남 아파트 상승", "임대 수익", "주택 공급 부족", "주택 구매 열풍", 
    "입주 물량 감소", "실거주 수요 증가", "외국인 투자 확대"
]

# Function to log in to Naver
def naver_login(driver, naver_id, naver_pw):
    driver.get("https://nid.naver.com/nidlogin.login")
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "id")))
        time.sleep(3)

        # Enter ID
        id_input = driver.find_element(By.ID, "id")
        pyperclip.copy(naver_id)
        id_input.click()
        id_input.send_keys(Keys.COMMAND + 'v')

        # Enter password
        password_input = driver.find_element(By.ID, "pw")
        pyperclip.copy(naver_pw)
        time.sleep(3)
        password_input.click()
        password_input.send_keys(Keys.COMMAND + 'v')

        # Click login button
        sign_in_button = driver.find_element(By.ID, "log.login")
        sign_in_button.click()
        time.sleep(3)
    except TimeoutException:
        print("Login timed out.")
        driver.quit()

def crawl_cafe(driver, keywords, start_date, end_date, output_file):
    driver.get("https://cafe.naver.com/jaegebal")
    time.sleep(3)
    
    driver.switch_to.default_content()
    print("[DEBUG] Returned to main content")
    search_bar = driver.find_element(By.ID, "topLayerQueryInput")
    search_bar.click()
    search_bar.clear()
    search_bar.send_keys("dummy")
    search_bar.send_keys(Keys.RETURN)
    time.sleep(3)

    data = []
    for keyword in keywords:  # keywords 리스트 내 검색어 순회
        try:
            print(f"Searching for keyword: {keyword}")
            driver.switch_to.frame("cafe_main")
            print("[DEBUG] Switched to iframe")
            # "제목만" 클릭
            select_box = driver.find_element(By.ID, "currentSearchByTop")
            select_box.click()

            # "제목만" 옵션 선택
            title_option = driver.find_element(By.XPATH, "//a[text()='제목만']")
            title_option.click()

            # 검색어 입력
            search_input = driver.find_element(By.ID, "queryTop")
            search_input.clear()  # 입력창 초기화
            search_input.send_keys(keyword)
            search_input.send_keys(Keys.RETURN)  # 검색 실행

            time.sleep(2)  # 검색 결과가 로드될 시간을 확보

            # 검색 결과 크롤링

            rows = driver.find_elements(By.CSS_SELECTOR, "#main-area > div:nth-child(5) > table > tbody > tr")  # 모든 행 선택
            print(f"[DEBUG] Found {len(rows)} rows")

            for row_index in range(len(rows)):
                try:
                    print(f"[DEBUG] Processing row {row_index + 1}")

                    rows = driver.find_elements(By.CSS_SELECTOR, "#main-area > div:nth-child(5) > table > tbody > tr")  # 모든 행 선택  
                    row = rows[row_index]

                    title_element = row.find_element(By.CSS_SELECTOR, "td.td_article .article")
                    title = title_element.text
                    print(f"[DEBUG] title: {title}")
                    link = title_element.get_attribute("href")
                    author = row.find_element(By.CSS_SELECTOR, "td.td_name .m-tcol-c").text
                    date = row.find_element(By.CSS_SELECTOR, "td.td_date").text
                    views = row.find_element(By.CSS_SELECTOR, "td.td_view").text

                    # content = ""
                    # 게시글 클릭 및 내용 수집
                    title_element.click()
                    time.sleep(2)

                    driver.switch_to.default_content()
                    driver.switch_to.frame("cafe_main")
                    
                    # content_element = driver.find_element(By.CLASS_NAME, "se-main-container")
                    # content = content_element.text

                    try:
                        content_element = driver.find_element(By.CLASS_NAME, "se-main-container")
                        content = content_element.text
                        print("[DEBUG] Content found")
                        print(f"{content}")
                        print("-" * 50)
                    except NoSuchElementException:
                        try: 
                            #app > div > div > div.ArticleContentBox > div.article_container
                            content_element = driver.find_element(By.CLASS_NAME, "txt")
                            content = content_element.text
                            print("[DEBUG] Outer Link found")
                            print(f"{content}")
                            print("-" * 50)
                        except NoSuchElementException:
                            try:
                                content_element = driver.find_element(By.CLASS_NAME, "scrap_added")
                                content = content_element.text
                                print("[DEBUG] Scrap found")
                                print(f"{content}")
                                print("-" * 50)
                            except NoSuchElementException:
                                try:
                                    content_element = driver.find_element(By.CLASS_NAME, "se-component-content")
                                    content = content_element.text
                                    print("[DEBUG] se-component-content found")
                                    print(f"{content}")
                                    print("-" * 50)
                                except NoSuchElementException:
                                    content = "Content not found"
                                    print("[ERROR] Content not found")
                    
                    driver.back()
                    time.sleep(2)
                    driver.switch_to.frame("cafe_main")
                    
                    # 날짜 필터링 및 데이터 저장
                    if start_date <= date <= end_date:
                        data.append([keyword, date, title, content, link, author, views])
                    
                    # print(f"[DEBUG] title: {title}")
                    # print(f"[DEBUG] link: {link}")
                    # print(f"[DEBUG] author: {author}")
                    # print(f"[DEBUG] date: {date}")
                    # print(f"[DEBUG] views: {views}")
                except StaleElementReferenceException:
                    print(f"[DEBUG] Stale element reference at row {row_index + 1}, retrying...")
                    rows = driver.find_elements(By.CSS_SELECTOR, "#main-area > div:nth-child(5) > table > tbody > tr")  # 모든 행 선택
                    row = rows[row_index]
                    title_element = row.find_element(By.CSS_SELECTOR, "td.td_article .article")
                    title = title_element.text
                    link = title_element.get_attribute("href")
                    author = row.find_element(By.CSS_SELECTOR, "td.td_name .m-tcol-c").text
                    date = row.find_element(By.CSS_SELECTOR, "td.td_date").text
                    views = row.find_element(By.CSS_SELECTOR, "td.td_view").text
                    
                    # 날짜 필터링 및 데이터 저장
                    if start_date <= date <= end_date:
                        data.append([keyword, date, title, content, link, author, views])
                    
                    # print(f"[DEBUG] title: {title}")
                    # print(f"[DEBUG] link: {link}")
                    # print(f"[DEBUG] author: {author}")
                    # print(f"[DEBUG] date: {date}")
                    # print(f"[DEBUG] views: {views}")
                except NoSuchElementException as e:
                    print(f"Error parsing row: {e}")


                # # 다음 페이지 이동
                # try:
                #     print("[DEBUG] 다음 페이지 이동")
                #     next_button = driver.find_