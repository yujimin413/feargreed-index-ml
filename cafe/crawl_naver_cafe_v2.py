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
    
    # Switch to iframe
    # driver.switch_to.frame("cafe_main")

    # Open search bar and collect data for each keyword
    data = []
    for keyword in keywords:
        # iframe에서 메인 페이지로 복귀
        driver.switch_to.default_content()
        print("[DEBUG] Returned to main content")
        # print(f"Searching for keyword: {keyword}")
        
        # Enter keyword into search bar
        search_bar = driver.find_element(By.ID, "topLayerQueryInput")
        search_bar.click()
        # print(f"[DEBUG] search_bar: {search_bar}")

        search_bar.clear()
        search_bar.send_keys(keyword)
        search_bar.send_keys(Keys.RETURN)
        time.sleep(3)
        print(f"Searching for keyword: {keyword}")

        # Iterate through pages of results
        while True:
            try:
                # Switch to the main iframe containing the search results
                driver.switch_to.frame("cafe_main")
                print("[DEBUG] Switched to iframe")

                # Locate all rows in the search result table
                # rows = driver.find_elements(By.CSS_SELECTOR, ".article-board.result-board.m-tcol-c table tbody tr")
                rows = driver.find_elements(By.CSS_SELECTOR, "tr")
                print(f"[DEBUG] Found {len(rows)} rows")

                for row in rows:
                    try:
                        # Extract post details
                        title_element = row.find_element(By.CSS_SELECTOR, "td.td_article .article")
                        title = title_element.text
                        link = title_element.get_attribute("href")
                        author = row.find_element(By.CSS_SELECTOR, "td.td_name .m-tcol-c").text
                        date = row.find_element(By.CSS_SELECTOR, "td.td_date").text
                        views = row.find_element(By.CSS_SELECTOR, "td.td_view").text
                        # Comments count might not exist; handle safely
                        try:
                            comments = row.find_element(By.CSS_SELECTOR, "td.td_article .list-i-cmt").text
                        except:
                            comments = "0"

                        print(f"[DEBUG] title: {title}")
                        print(f"[DEBUG] link: {link}")
                        print(f"[DEBUG] author: {author}")
                        print(f"[DEBUG] date: {date}")
                        print(f"[DEBUG] views: {views}")
                        print(f"[DEBUG] comments: {comments}")

                        # Filter by date
                        if start_date <= date <= end_date:
                            data.append([keyword, title, link, author, date, views, comments])
                    except Exception as e:
                        print(f"Error parsing row: {e}")

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
        writer.writerow(["Keyword", "Title", "Link", "Author", "Date", "Views", "Comments"])
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
