import time
import csv
import json
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import tweepy
# Twitter API 설정
# API Key와 Secret 등은 사용자가 직접 입력해야 합니다.
API_KEY = "7gwenBY6QhMz2Rf1sJwtOMbna"
API_SECRET = "uyIcPhIAKPDYg20cFgbgD8fCr3Bl1byDJeMItWO41pY3CJKYRY"
ACCESS_TOKEN = "1880843773724528640-0E08hKi7JQj9TRMJG2cGYSWCVJfmD2"
ACCESS_TOKEN_SECRET = "dJ0ZoboFcYpKveEA4w3NIpKV9nZUA1qsqKBUgfnc2YPQy"
# Twitter API 인증 설정
def authenticate_twitter_api():
    auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    return api

# API를 사용하여 데이터 수집
def fetch_twitter_data_via_api(api, query, start_date, end_date, lang="ko", max_results=100):
    tweets = []
    for status in tweepy.Cursor(api.search_tweets, 
                                q=query, 
                                lang=lang, 
                                since=start_date, 
                                until=end_date, 
                                tweet_mode="extended").items(max_results):
        tweets.append({
            "content": status.full_text,
            "author": status.user.screen_name,
            "created_at": status.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "retweets": status.retweet_count,
            "likes": status.favorite_count,
        })
    return tweets
# Selenium 설정 및 로그인
CHROME_DRIVER_PATH = "./chromedriver"  # ChromeDriver 경로를 사용자 환경에 맞게 수정하세요
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
service = Service(CHROME_DRIVER_PATH)
def setup_selenium_driver():
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def login_to_twitter(driver, username, password):
    driver.get("https://x.com/login")
    time.sleep(5)  # 페이지 로딩 대기
    
    username_input = driver.find_element(By.NAME, "session[username_or_email]")
    password_input = driver.find_element(By.NAME, "session[password]")

    username_input.send_keys(username)
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)
    time.sleep(5)  # 로그인 후 로딩 대기

# Selenium을 사용하여 데이터 크롤링
def fetch_twitter_data_via_selenium(driver, query, lang="ko", max_scrolls=10):
    tweets = []
    driver.get(f"https://x.com/search?q={query}&lang={lang}")
    time.sleep(5)  # 초기 로딩 대기

    for _ in range(max_scrolls):
        tweets_elements = driver.find_elements(By.CSS_SELECTOR, "article")
        for tweet in tweets_elements:
            try:
                content = tweet.find_element(By.CSS_SELECTOR, "div[lang]").text
                author = tweet.find_element(By.CSS_SELECTOR, "div[dir=ltr]").text
                created_at = "Unknown"  # Selenium으로 시간 정보를 직접 가져오기 어려운 경우
                retweets = tweet.find_element(By.CSS_SELECTOR, "div[data-testid='retweet']").text
                likes = tweet.find_element(By.CSS_SELECTOR, "div[data-testid='like']").text

                tweets.append({
                    "content": content,
                    "author": author,
                    "created_at": created_at,
                    "retweets": retweets,
                    "likes": likes,
                })
            except Exception as e:
                print(f"Error extracting tweet: {e}")

        # 무한 스크롤
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

    return tweets

def fetch_twitter_data_v2(api, query, start_time, end_time, lang="ko", max_results=100):
    tweets = []
    try:
        response = api.search_recent_tweets(
            query=query,
            start_time=start_time,
            end_time=end_time,
            max_results=max_results,
            tweet_fields=["created_at", "author_id", "public_metrics", "text"],
            expansions=["author_id"]
        )
        for tweet in response.data:
            tweets.append({
                "content": tweet.text,
                "author_id": tweet.author_id,
                "created_at": tweet.created_at,
                "retweets": tweet.public_metrics["retweet_count"],
                "likes": tweet.public_metrics["like_count"],
            })
    except Exception as e:
        print(f"Error fetching tweets: {e}")
    return tweets


# 결과를 CSV로 저장
def save_to_csv(tweets, filename):
    keys = tweets[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(tweets)


# # 실행 예시
# def main():
#     # Twitter API 데이터 수집
#     api = authenticate_twitter_api()
#     api_tweets = fetch_twitter_data_via_api(api, "부동산", "2024-01-01", "2024-01-31")
#     save_to_csv(api_tweets, "twitter_api_data.csv")

#     # Selenium 데이터 수집
#     driver = setup_selenium_driver()
#     login_to_twitter(driver, "your_email", "your_password")
#     selenium_tweets = fetch_twitter_data_via_selenium(driver, "부동산")
#     save_to_csv(selenium_tweets, "twitter_selenium_data.csv")
#     driver.quit()

# if __name__ == "__main__":
#     main()

# def main():
#     # Twitter API 데이터 수집 (v2 사용)
#     api = authenticate_twitter_api()
#     api_tweets = fetch_twitter_data_v2(api, "부동산", "2024-01-01T00:00:00Z", "2024-01-31T23:59:59Z")
#     save_to_csv(api_tweets, "twitter_api_data_v2.csv")

#     # Selenium 데이터 수집
#     driver = setup_selenium_driver()
#     login_to_twitter(driver, "your_email", "your_password")
#     selenium_tweets = fetch_twitter_data_via_selenium(driver, "부동산")
#     save_to_csv(selenium_tweets, "twitter_selenium_data.csv")
#     driver.quit()


import pandas as pd

def main():
    # Twitter API 데이터 수집 (v2 사용)
    api = authenticate_twitter_api()
    api_tweets = fetch_twitter_data_v2(api, "부동산", "2024-01-01T00:00:00Z", "2024-01-31T23:59:59Z")
    
    # API 데이터를 Pandas DataFrame으로 변환하여 출력
    if api_tweets:
        api_df = pd.DataFrame(api_tweets)
        print("API 데이터 미리보기:")
        print(api_df.head())  # 상위 5개 데이터 미리보기
    else:
        print("API로 수집된 데이터가 없습니다.")
    
    # CSV로 저장
    save_to_csv(api_tweets, "twitter_api_data_v2.csv")

    # Selenium 데이터 수집
    driver = setup_selenium_driver()
    login_to_twitter(driver, "your_email", "your_password")
    selenium_tweets = fetch_twitter_data_via_selenium(driver, "부동산")
    
    # Selenium 데이터를 Pandas DataFrame으로 변환하여 출력
    if selenium_tweets:
        selenium_df = pd.DataFrame(selenium_tweets)
        print("Selenium 데이터 미리보기:")
        print(selenium_df.head())  # 상위 5개 데이터 미리보기
    else:
        print("Selenium으로 수집된 데이터가 없습니다.")
    
    # CSV로 저장
    save_to_csv(selenium_tweets, "twitter_selenium_data.csv")
    driver.quit()
