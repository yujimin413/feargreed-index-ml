import os
import time
from datetime import datetime, timedelta
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import re

# 키워드 리스트
keywords = [
    "공포", "집값 폭락"
]

# 날짜 설정
start_date = "2020-01-01"
end_date = "2024-12-31"

# 네이버 뉴스 URL
naver_url = "https://search.naver.com/search.naver?where=news"

# 크롤링 결과 저장 리스트
results = []

def calculate_quarter(date_str):
    """날짜 문자열로부터 분기 계산"""
    try:
        date = pd.to_datetime(date_str, errors="coerce")
        year = date.year % 100  # 두 자리 연도로 변환
        quarter = (date.month - 1) // 3 + 1
        return f"{year}년{quarter}분기"
    except Exception:
        return "날짜 오류"
    
def parse_date(date_str):
    """날짜 문자열을 yyyy-mm-dd 형식으로 변환"""
    try:
        # "숫자 주|일|시간 전" 형식 처리
        if "전" in date_str:
            current_date = datetime.now()
            if "주 전" in date_str:
                weeks = int(date_str.split("주")[0])
                parsed_date = current_date - timedelta(weeks=weeks)
            elif "일 전" in date_str:
                days = int(date_str.split("일")[0])
                parsed_date = current_date - timedelta(days=days)
            elif "시간 전" in date_str:
                hours = int(date_str.split("시간")[0])
                parsed_date = current_date - timedelta(hours=hours)
            else:
                return "날짜 오류"
            return parsed_date.strftime("%Y.%m.%d")
        # yyyy.mm.dd. 형식 처리
        elif "." in date_str:
            parsed_date = datetime.strptime(date_str.strip(), "%Y.%m.%d")
            return parsed_date.strftime("%Y.%m.%d")
        else:
            return "날짜 오류"
    except Exception:
        return "날짜 오류"

# 날짜 정수 변환 함수
def remove_leading_zero(date_component):
    return str(int(date_component))  # 정수로 변환 후 문자열로 다시 변환

def get_articles(keyword, driver):
    """키워드로 뉴스 크롤링"""
    global results
    driver.get(naver_url)
    time.sleep(2)
    
    # 검색창에 키워드 입력
    try:
        print("[DEBUG] 검색창 로드 대기 중...")
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "query"))
        )
        print("[DEBUG] 검색창 로드 완료!")
        search_box.clear()
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)
        time.sleep(2)
    except Exception as e:
        print(f"[DEBUG] 검색창 처리 중 에러: {e}")
        return

    # 옵션 버튼 클릭
    try:
        print("[DEBUG] 옵션 버튼 찾는 중...")
        option_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn_option._search_option_open_btn"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option_button)
        option_button.click()
        print("[DEBUG] 옵션 버튼 클릭 완료!")
        time.sleep(2)
    except Exception as e:
        print(f"[ERROR] 옵션 버튼 처리 중 에러: {e}")
        return

    # 날짜 필터 적용
    try:
        print("[DEBUG] 직접 입력 버튼 찾는 중...")
        date_input_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.txt_option._calendar_select_trigger"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", date_input_button)
        date_input_button.click()
        print("[DEBUG] 직접 입력 버튼 클릭 완료!")
        time.sleep(3)

        # 시작 날짜 설정
        print("[DEBUG] 시작 날짜 설정 중...")
        start_date_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a._start_trigger"))
        )
        start_date_button.click()
        time.sleep(3)

        print(f"before - START DATE: {start_date.split('-')[0]}년 {start_date.split('-')[1]}월 {start_date.split('-')[2]}일")


        start_year_val = remove_leading_zero(start_date.split('-')[0])
        start_month_val = remove_leading_zero(start_date.split('-')[1])
        start_day_val = remove_leading_zero(start_date.split('-')[2])

        print(f"after - START DATE: {start_year_val}년 {start_month_val}월 {start_day_val}일")

        start_year = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[@class='link' and text()='{start_year_val}']"))
        )
        start_year.click()
        time.sleep(3)

        start_month = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[@class='link' and text()='{start_month_val}']"))
        )
        start_month.click()
        time.sleep(3)

        # start_day = WebDriverWait(driver, 10).until(
        #     EC.element_to_be_clickable((By.XPATH, f"//a[@class='link' and text()='{start_day_val}']"))
        # )
        start_day = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//li[@data-value='{start_day_val}']/a"))
        )
        start_day.click()
        time.sleep(3)

        # 종료 날짜 설정
        print("[DEBUG] 종료 날짜 설정 중...")
        end_date_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a._end_trigger"))
        )
        end_date_button.click()
        time.sleep(3)

        end_year_val = end_date.split('-')[0]
        end_month_val = remove_leading_zero(end_date.split('-')[1])
        end_day_val = remove_leading_zero(end_date.split('-')[2])

        print(f"END DATE: {end_year_val}년 {end_month_val}월 {end_day_val}일")

        end_year = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[@class='link' and text()='{end_year_val}']"))
        )
        end_year.click()
        time.sleep(3)

        end_month = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[@class='link' and text()='{end_month_val}']"))
        )
        end_month.click()
        time.sleep(3)

        end_day = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[@class='link' and text()='{end_day_val}']"))
        )
        end_day.click()
        time.sleep(3)

        # 적용 버튼 클릭
        print("[DEBUG] 적용 버튼 클릭 중...")
        apply_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn_apply._apply_btn"))
        )
        apply_button.click()
        print("[DEBUG] 적용 버튼 클릭 완료!")
        time.sleep(2)

        # 날짜 적용 확인
        applied_date_element = driver.find_element(By.CSS_SELECTOR, "a.txt_option._calendar_select_trigger")
        applied_date = applied_date_element.text.strip()  # 텍스트 가져오기
        print(f"[DEBUG] 적용된 날짜 텍스트 원본: {applied_date}")

        # 정규식으로 날짜 추출
        date_pattern = re.search(r"(\d{4}\.\d{2}\.\d{2})\.\s~\s(\d{4}\.\d{2}\.\d{2})\.", applied_date)
        # applied_dates = re.search(date_pattern, applied_date)

        # if not applied_dates:
        #     print(f"[DEBUG] 적용된 날짜 텍스트를 분석할 수 없습니다. 원본 텍스트: {applied_date}")
        #     raise Exception("적용된 날짜를 파싱하지 못했습니다.")
        
        # 날짜 추출 및 변수에 할당
        if date_pattern:
            parsed_start_date = (date_pattern.group(1)).replace('.', '-')
            parsed_end_date = (date_pattern.group(2)).replace('.', '-')
            print(f"parsed_start_date = {parsed_start_date}")
            print(f"parsed_end_date = {parsed_end_date}")
            print(f"start_date = {start_date}")
            print(f"end_date = {end_date}")
            # exit()
        else:
            print("날짜 형식이 올바르지 않습니다.")
        
        # parsed_start_date, parsed_end_date = applied_dates.groups()
        # print(f"[DEBUG] 파싱된 시작 날짜: {parsed_start_date}, 종료 날짜: {parsed_end_date}")

        # 비교
        if parsed_start_date != start_date or parsed_end_date != end_date:
            print("[ERROR] 적용된 날짜와 설정된 날짜가 일치하지 않습니다.")
            raise Exception("날짜 필터가 올바르게 설정되지 않았습니다.")
        # 페이지 새로고침
        print("[DEBUG] 페이지 새로고침 중...")
        driver.refresh()
        time.sleep(3)  # 새로고침 후 안정적인 로드 시간을 보장하기 위해 대기
        # exit()
    except Exception as e:
        print(f"[ERROR] 날짜 필터 적용 중 에러: {e}")
        return

    print("[INFO] 크롤링을 시작합니다...")
    # 뉴스 기사 크롤링
    page = 1
    while True:
        try:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            articles = soup.select("ul.list_news > li")
            
            if not articles:
                break
            
            for article in articles:
                try:
                    title = article.select_one("a.news_tit").get_text()
                    url = article.select_one("a.news_tit")["href"]
                    content = article.select_one("div.news_dsc").get_text() if article.select_one("div.news_dsc") else "내용 없음"
                    press = article.select_one("a.info.press").get_text() if article.select_one("a.info.press") else "출처 없음"            
                    raw_date = article.select_one("span.info").get_text() if article.select_one("span.info") else "날짜 없음"
                    parsed_date = parse_date(raw_date)
                    quarter = calculate_quarter(parsed_date)
                    
                    results.append({
                        "키워드": keyword,
                        "분기": quarter,
                        "작성일": parsed_date,
                        "제목": title,
                        "내용": content,
                        "URL": url,
                        "기자 이름": press
                    })
                except Exception as e:
                    print("[ERROR] 기사 처리 중 에러:", e)
            
            # 다음 페이지로 이동
            next_button = soup.select_one("a.btn_next")
            if next_button and "href" in next_button.attrs:
                driver.get("https://search.naver.com" + next_button["href"])
                time.sleep(2)
            else:
                break
            page += 1
        except Exception as e:
            print(f"[ERROR] 페이지 크롤링 중 에러: {e}")
            break

def generate_filename(base_name, extension="xlsx"):
    """파일명을 날짜, 시간 기반으로 생성하고 중복 시 숫자를 추가"""
    # 현재 날짜와 시간 가져오기 (YYMMDD_HHMM 형식)
    timestamp = datetime.now().strftime("%y%m%d_%H%M")
    filename = f"{base_name}_{timestamp}.{extension}"
    
    # 중복 파일명 처리
    counter = 1
    while os.path.exists(filename):
        filename = f"{base_name}_{timestamp}({counter}).{extension}"
        counter += 1
    
    return filename

def main():
    # Selenium WebDriver 설정
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 브라우저를 띄우지 않고 실행
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    # 키워드별로 기사 수집
    for keyword in keywords:
        print(f"[INFO] '{keyword}' 키워드로 크롤링 중")
        get_articles(keyword, driver)

    # Selenium 드라이버 종료
    driver.quit()

    # 데이터프레임으로 변환 및 저장
    df = pd.DataFrame(results)
    output_file = generate_filename("naver_news_crawling")
    df.to_excel(output_file, index=False)
    print(f"[INFO] 크롤링 완료. 결과가 {output_file}에 저장되었습니다.")

if __name__ == "__main__":
    main()