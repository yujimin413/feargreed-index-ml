# 네이버 뉴스 크롤링
# 참고 링크: https://github.com/sbomhoo/naver_news_crawling

# 사용법: keywords 리스트에 크롤링할 키워드 추가, 파일명 설정 후 실행


# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import pandas as pd
import re
import os

# 각 크롤링 결과 저장하기 위한 리스트 선언
title_text = []
link_text = []
source_text = []
date_text = []
contents_text = []
result = {}

# 엑셀로 저장하기 위한 변수
RESULT_PATH = './'  # 결과 저장할 경로
now = datetime.now()  # 파일이름 현 시간으로 저장하기

# 내용 정제화 함수
def contents_cleansing(contents):
    first_cleansing_contents = re.sub('<dl>.*?</a> </div> </dd> <dd>', '', 
                                      str(contents)).strip()  # 앞에 필요없는 부분 제거
    second_cleansing_contents = re.sub('<ul class="relation_lst">.*?</dd>', '', 
                                       first_cleansing_contents).strip()  # 뒤에 필요없는 부분 제거 (새끼 기사)
    third_cleansing_contents = re.sub('<.+?>', '', second_cleansing_contents).strip()
    contents_text.append(third_cleansing_contents)

def crawler(maxpage, query, sort, s_date, e_date, output_file):
    global title_text, link_text, source_text, date_text, contents_text  # 전역 리스트 초기화

    s_from = s_date.replace(".", "")
    e_to = e_date.replace(".", "")
    page = 1  
    maxpage_t = (int(maxpage) - 1) * 10 + 1  # 11=2페이지, 21=3페이지 ...

    while page <= maxpage_t:
        url = f"https://search.naver.com/search.naver?where=news&query={query}&sort={sort}&ds={s_date}&de={e_date}&nso=so%3Ar%2Cp%3Afrom{s_from}to{e_to}%2Ca%3A&start={page}"
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        # <a>태그에서 제목과 링크주소 추출
        atags = soup.select('.news_tit')
        for atag in atags:
            title_text.append(atag.text)  # 제목
            link_text.append(atag['href'])  # 링크주소

        # 신문사 추출
        source_lists = soup.select('.info_group > .press')
        for source_list in source_lists:
            source_text.append(source_list.text)  # 신문사

        # 날짜 추출
        date_lists = soup.select('.info_group > span.info')
        for date_list in date_lists:
            if date_list.text.find("면") == -1:
                date_text.append(date_list.text)

        # 본문요약본
        contents_lists = soup.select('.news_dsc')
        for contents_list in contents_lists:
            contents_cleansing(contents_list)  # 본문요약 정제화

        page += 10

    # 모든 리스트 딕셔너리 형태로 저장
    result = {
        "keyword": query,
        "date": date_text,
        "title": title_text,
        "source": source_text,
        "contents": contents_text,
        "link": link_text
    }

    df = pd.DataFrame(result)  # DataFrame으로 변환

    # 파일이 존재하면 데이터 추가, 없으면 새로 생성
    if os.path.exists(output_file):
        existing_df = pd.read_csv(output_file)
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        combined_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    else:
        df.to_csv(output_file, index=False, encoding='utf-8-sig')

    print(f"크롤링 완료: 키워드='{query}', 저장 파일='{output_file}'")

def main():
    info_main = input("="*50 + "\n" + "입력 형식에 맞게 입력해주세요." + "\n" + " 시작하시려면 Enter를 눌러주세요." + "\n" + "="*50)

    maxpage = input("최대 크롤링할 페이지 수 입력하시오: ")  
    sort = input("뉴스 검색 방식 입력(관련도순=0  최신순=1  오래된순=2): ")  # 관련도순=0  최신순=1  오래된순=2
    s_date = input("시작날짜 입력(2019.01.04):")  # 2019.01.04
    e_date = input("끝날짜 입력(2019.01.05):")   # 2019.01.05

    # 검색어 리스트
    keywords = [
        # 탐욕 키워드
        "집값 상승", "부동산 호황", "매수 타이밍", "재건축 기대", "저금리 효과",
        "개발 호재", "시장 회복", "신규 분양 열기", "자산 가치 상승", "투자 기회",
        "강남 아파트 상승", "임대 수익", "주택 공급 부족", "주택 구매 열풍", 
        "입주 물량 감소", "실거주 수요 증가", "외국인 투자 확대"
    ]

    # 파일 이름 설정
    timestamp = datetime.now().strftime("%y%m%d_%H%M")
    output_file = f"{RESULT_PATH}news_crawl_POSITIVE_{timestamp}.csv"

    for query in keywords:
        print(f"크롤링 시작: 키워드='{query}'")
        crawler(maxpage, query, sort, s_date, e_date, output_file)

# 메인 함수 호출
main()
