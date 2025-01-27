# cafe_data_250127_2136.csv
# 키워드별 수집, content 수집 됨 
# 페이징 기능 추가함
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
    "부동산 호황"
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
            # "제목만" 옵션 선택
            title_option = driver.find_element(By.XPATH, "//a[text()='제목만']")
            title_option.click()
            # 검색어 입력
            search_input = driver.find_element(By.ID, "queryTop")
            search_input.clear()  # 입력창 초기화
            search_input.send_keys(keyword)
            search_input.send_keys(Keys.RETURN)  # 검색 실행
            time.sleep(1)  # 검색 결과가 로드될 시간을 확보

            while True:  # 페이지 그룹 순회 (예: 1~10, 11~20 등)
                page_buttons = driver.find_elements(By.CSS_SELECTOR, ".prev-next a:not(.pgR)")  # 페이지 번호 버튼들
                page_count = len(page_buttons)
                
                for page_index in range(page_count):  # 각 페이지 번호 클릭
                    print(f"[DEBUG] Crawling page {page_index + 1} for keyword: {keyword}")
                    
                    # 페이지 버튼 리스트를 다시 찾는다 (DOM 업데이트로 인해 필요)
                    page_buttons = driver.find_elements(By.CSS_SELECTOR, ".prev-next a:not(.pgR)")
                    page_buttons[page_index].click()
                    time.sleep(1)  # 페이지 로드 대기

                    rows = driver.find_elements(By.CSS_SELECTOR, "#main-area > div:nth-child(5) > table > tbody > tr")  # 모든 행 선택
                    print(f"[DEBUG] Found {len(rows)} rows")

                    for row_index in range(len(rows)):
                        try:
                            rows = driver.find_elements(By.CSS_SELECTOR, "#main-area > div:nth-child(5) > table > tbody > tr")
                            row = rows[row_index]

                            title_element = row.find_element(By.CSS_SELECTOR, "td.td_article .article")
                            title = title_element.text
                            print(f"[DEBUG] Title: {title}")
                            link = title_element.get_attribute("href")
                            author = row.find_element(By.CSS_SELECTOR, "td.td_name .m-tcol-c").text
                            date = row.find_element(By.CSS_SELECTOR, "td.td_date").text
                            if date < start_date or date > end_date:
                                print(f"[DEBUG] Date out of range: {date}")
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
                            time.sleep(1)
                            driver.switch_to.frame("cafe_main")

                            # # 날짜 필터링 및 데이터 저장
                            # if start_date <= date <= end_date:
                            #     data.append([keyword, date, title, content, link, author, views])
                            
                            
                            data.append([keyword, date, title, content, link, author, views])

                        except Exception as e:
                            print(f"[DEBUG] Error processing row {row_index + 1}: {e}")

                # "다음" 버튼 클릭 (페이지 그룹 이동)
                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, ".prev-next a.pgR")
                    next_button.click()
                    time.sleep(1)
                except NoSuchElementException:
                    print(f"No more pages for keyword: {keyword}")
                    break  # 다음 키워드로 넘어감

        except NoSuchElementException as e:
            print(f"Error switching to iframe or finding rows: {e}")
        
        driver.switch_to.default_content()

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
    output_file = f"cafe_data_{timestamp}.csv"

    # Initialize WebDriver
    driver = webdriver.Chrome()  # Ensure chromedriver is in your PATH

    try:
        naver_login(driver, NAVER_ID, NAVER_PW)
        crawl_cafe(driver, keywords, start_date, end_date, output_file)
    finally:
        driver.quit()
