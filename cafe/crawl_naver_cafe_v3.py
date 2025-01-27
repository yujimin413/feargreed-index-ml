# 네이버 카페에서 특정 키워드로 검색한 결과를 크롤링하는 스크립트
# 크롤링 대상: 제목, 링크, 작성자, 작성일, 조회수, 댓글수
# 크롤링 결과를 CSV 파일로 저장

# 키워드별로 저장하지만 페이지 못넘어가는듯

# cafe_data_250127_1413.csv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

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
    "집값 상승", "부동산 호황"
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

# Function to search for keywords and collect data
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

            for idx, row in enumerate(rows):
                try:
                    print(f"[DEBUG] Processing row {idx + 1}")
                    # 게시글 링크 선택: a.article이 있으면 사용, 없으면 기본 a 태그 선택
                    try:
                        # title_element = row.find_element(By.CSS_SELECTOR, "a.article")
                        
                        title_element = row.find_element(By.CSS_SELECTOR, f"#main-area > div:nth-child(5) > table > tbody > tr:nth-child({idx + 1}) > td.td_article > div.board-list > div > a.article")
                    except NoSuchElementException:
                        # title_element = row.find_element(By.CSS_SELECTOR, "a")
                        title_element = row.find_element(By.CSS_SELECTOR, f"#main-area > div:nth-child(5) > table > tbody > tr:nth-child({idx + 1}) > td.td_article > div.board-list > div > a")
                # try:
                #     # 제목 요소 탐색
                #     try:
                #         title_element = row.find_element(By.CSS_SELECTOR, "td.td_article > div.board-list > div > a.article")
                #     except NoSuchElementException:
                #         # 기본 `a` 요소로 대체 검색
                #         title_element = row.find_element(By.CSS_SELECTOR, "td.td_article > div.board-list > div > a")
                    
                    title = title_element.text
                    link = title_element.get_attribute("href")

                    # 나머지 데이터 수집
                    author = row.find_element(By.CSS_SELECTOR, "td.td_name .m-tcol-c").text
                    date = row.find_element(By.CSS_SELECTOR, "td.td_date").text
                    views = row.find_element(By.CSS_SELECTOR, "td.td_view").text

                    # 게시글 클릭 및 내용 수집
                    title_element.click()
                    time.sleep(2)
                    try:
                        content = driver.find_element(By.CLASS_NAME, "se-main-container").text
                    except NoSuchElementException:
                        content = "[ERROR] Content not found"
                    driver.back()
                    time.sleep(2)
                    driver.switch_to.frame("cafe_main")

                    print(f"[DEBUG] Collected data:\n제목: {title}\n작성자: {author}\n날짜: {date}\n조회수: {views}\n내용: {content[:100]}...\n")

                    # 날짜 필터링 및 데이터 저장
                    if start_date <= date <= end_date:
                        data.append([keyword, title, link, author, date, views, content])

                except NoSuchElementException as e:
                    print(f"[DEBUG] Element not found for row {idx + 1}: {e}. Skipping...")
                    continue
                driver.switch_to.default_content()


            
#             exit()
#             ###
#             rows = driver.find_elements(By.CSS_SELECTOR, "#main-area > div:nth-child(5) > table > tbody > tr")  # 모든 행 선택
#             print(f"[DEBUG] Found {len(rows)} rows")
#             for idx, row in enumerate(rows):
#                 try:
#                     # `nth-child`를 활용하여 행의 제목 요소를 정확히 선택
#                     title_element = driver.find_element(
#                         By.CSS_SELECTOR, f"#main-area > div:nth-child(5) > table > tbody > tr:nth-child({idx + 1}) > td.td_article > div.board-list > div > a.article"
#                     )
#                     title = title_element.text
#                     link = title_element.get_attribute("href")

#                     # 나머지 데이터 수집
#                     author = row.find_element(By.CSS_SELECTOR, "td.td_name .m-tcol-c").text
#                     date = row.find_element(By.CSS_SELECTOR, "td.td_date").text
#                     views = row.find_element(By.CSS_SELECTOR, "td.td_view").text

#                     # 게시글 클릭 및 내용 수집
#                     title_element.click()
#                     time.sleep(2)
#                     try:
#                         content = driver.find_element(By.CLASS_NAME, "se-main-container").text
#                     except NoSuchElementException:
#                         content = "[ERROR] Content not found"
#                     driver.back()
#                     time.sleep(5)

#                     print(f"[DEBUG] Collected data:\n제목:{title}\n작성자:{author}\n날짜:{date}\n조회수:{views}\n내용:{content[:100]}...\n")

#                     # 날짜 필터링 및 데이터 저장
#                     if start_date <= date <= end_date:
#                         data.append([keyword, title, link, author, date, views, content])

#                 except NoSuchElementException:
#                     print(f"[DEBUG] Element not found for row {idx + 1}. Skipping...")
#                     continue
            
#             exit()

#             ### 

#             for idx, row in enumerate(rows):
#                 try:
#                     # 디버깅용으로 HTML 출력
#                     print(f"[DEBUG] Row {idx + 1} HTML: {row.get_attribute('outerHTML')}")

#                     # `a.article` 요소가 있는지 확인
#                     title_element = row.find_element(By.CSS_SELECTOR, f"{idx+1} a.article")
#                     title = title_element.text
#                     link = title_element.get_attribute("href")
#                     print(f"[DEBUG] Found title: {title}")
#                     # 다른 정보 수집
#                     author = row.find_element(By.CSS_SELECTOR, "td.td_name .m-tcol-c").text
#                     date = row.find_element(By.CSS_SELECTOR, "td.td_date").text
#                     views = row.find_element(By.CSS_SELECTOR, "td.td_view").text

#                     # 게시글 내용 추출
#                     title_element.click()
#                     time.sleep(2)  # 페이지 로드 시간 대기
#                     content = driver.find_element(By.CLASS_NAME, "se-main-container").text
#                     driver.back()
#                     time.sleep(2)  # 뒤로가기 대기

#                     # 데이터 저장
#                     print(f"[DEBUG] Collected data: {title}, {author}, {date}, {views}, {content[:100]}...")
#                 except NoSuchElementException:
#                     print(f"[DEBUG] `a.article` not found in row {idx + 1}. Skipping...")
#                     continue
#                 except Exception as e:
#                     print(f"[DEBUG] Error in row {idx + 1}: {e}")
#                     continue

#             exit()
# ###
#             for row in rows:
#                 try:
#                     print(f"[DEBUG] row: {row}")
                    
#                     # Extract post details
#                     title_element = row.find_element(By.CSS_SELECTOR, "a.article")
#                     title = title_element.text
#                     link = title_element.get_attribute("href")
#                     author = row.find_element(By.CSS_SELECTOR, "td.td_name .m-tcol-c").text
#                     date = row.find_element(By.CSS_SELECTOR, "td.td_date").text
#                     views = row.find_element(By.CSS_SELECTOR, "td.td_view").text
#                     # Comments count might not exist; handle safely
#                     try:
#                         comments = row.find_element(By.CSS_SELECTOR, "td.td_article .list-i-cmt").text
#                     except:
#                         comments = "0"

#                     # 클릭하여 게시글 내용 가져오기
#                     title_element.click()
#                     time.sleep(2)

#                     try:
#                         content = driver.find_element(By.CLASS_NAME, "se-main-container").text
#                     except:
#                         content = "[ERROR] Unable to extract contents"

#                     # 뒤로가기
#                     driver.back()
#                     time.sleep(2)

#                     print(f"[DEBUG] title: {title}")
#                     print(f"[DEBUG] link: {link}")
#                     print(f"[DEBUG] author: {author}")
#                     print(f"[DEBUG] date: {date}")
#                     print(f"[DEBUG] views: {views}")
#                     print(f"[DEBUG] comments: {comment}")
#                     print(f"[DEBUG] contents: {content[:100]}...")  # 내용의 일부 출력

#                     # Filter by date
#                     if start_date <= date <= end_date:
#                         data.append([keyword, date, title, content, link, author, views, comments])
#                 except Exception as e:
#                     print(f"Error parsing row: {e}")
#                     exit()

            # Check for and click the "next" button
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, ".prev-next a.next")
                next_button.click()
                time.sleep(3)
            except Exception:
                print(f"No more pages for keyword: {keyword}")
                break
        except Exception as e:
            print(f"Error during page processing: {e}")
            break



    # Save to CSV
    with open(output_file, mode="w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Keyword", "Date", "Title", "Content", "Link", "Author", "Views", "Comments"])
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
