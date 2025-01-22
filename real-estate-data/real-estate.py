import requests
import urllib.parse

def main() :
    # API 요청 정보
    LAWD_CD = 11110  # 지역코드 (숫자)
    DEAL_YMD = 202407  # 계약연월 (숫자)
    serviceKey_decoding = "iDsEbBq1YeWuOJeS5oxnDsz5ciDol0NWD+yNthbF69+FZz16yaxhqGLo3aA5FGyt9kcHpkUM2oZXYucwBAJjXQ=="  # 디코딩된 인증키
    pageNo = 1  # 페이지 번호 (선택)
    numOfRows = 10  # 페이지 당 결과 수 (선택)

    # serviceKey를 URL 인코딩
    serviceKey_encoding = urllib.parse.quote(serviceKey_decoding)
    # print(f"{serviceKey_encoding}")

    # 요청 URL 생성
    url = f"https://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade"
    params = {
        "LAWD_CD": LAWD_CD,
        "DEAL_YMD": DEAL_YMD,
        "serviceKey": serviceKey_encoding,
        "pageNo": pageNo,
        "numOfRows": numOfRows,
    }

    # GET 요청 보내기
    response = requests.get(url, params=params)

    # 응답 확인 및 처리
    if response.status_code == 200:
        print("Request was successful.")
        print("Response Data:")
        print(response.text)  # XML 데이터 출력
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        
if __name__ == '__main__':
    main()
   