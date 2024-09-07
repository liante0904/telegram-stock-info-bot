
import requests
from bs4 import BeautifulSoup


def check_market_status(market):
    
    api_url = f'https://m.stock.naver.com/api/index/{market}/basic'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        api_response = requests.get(api_url, headers=headers)
        if api_response.status_code == 200:
            stock_basic_data = api_response.json()
            return stock_basic_data['marketStatus']
        else:
            return {}
    except Exception as e:
        print(f"Error fetching API data: {e}")
        return {}

print(check_market_status(market='KOSPI'))
# def check_market_status(url):
#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # 요청이 성공했는지 확인

#         soup = BeautifulSoup(response.text, 'html.parser')

#         # 예를 들어, 페이지에서 특정 클래스를 가진 요소를 찾는다고 가정
#         status_element = soup.find(class_='market-status')  # 이 부분은 실제 페이지 구조에 맞게 수정해야 함

#         if status_element:
#             status_text = status_element.get_text(strip=True)
#             if '장운영' in status_text:
#                 return "장운영 중"
#             else:
#                 return "장운영 중이지 않음"
#         else:
#             return "상태를 찾을 수 없음"

#     except requests.RequestException as e:
#         return f"요청 중 오류 발생: {e}"

# 사용 예시
# url = 'https://m.stock.naver.com/api/index/KOSPI/integration'
# print(check_market_status(url))

# # {'종목명': '삼성전자', 'PER': 18.16, 'fwdPER': 12.56, 'PBR': 1.35, '배당수익률': 1.94, 
# # '예상배당수익률': 2.04, 'ROE': 10.84, '현재가': 74300, '전일비': 300, '등락률': 0.41, 
# # '비고(메모)': ' ', '1D': 0.41, '1W': -4.38, '1M': -6.66, '3M': -1.85, '6M': 0.81, 
# # 'YTD': -5.35, '1Y': 4.65, '종목코드': '005930', 
# # '네이버url': 'https://finance.naver.com/item/main.naver?code=005930'}
# from module.naver_upjong_quant import fetch_stock_info_quant_API
# fetch_stock_info_quant_API('005930')



# import time
# import requests
# from bs4 import BeautifulSoup

# def fetch_stock_info_quant(stock_code):
#     url = f'https://finance.naver.com/item/main.naver?code={stock_code}'
    
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#     }
    
#     # HTTP 요청
#     response = requests.get(url, headers=headers)
#     response.encoding = 'euc-kr'
    
#     if response.status_code == 200:
#         # 페이지 내용 파싱
#         soup = BeautifulSoup(response.text, 'html.parser')
#         # 특정 데이터를 추출하는 코드가 여기에 들어갈 수 있습니다.
#         return soup
#     else:
#         return {}

# def fetch_stock_info_quant_API(stock_code):
#     api_url = f'https://m.stock.naver.com/api/stock/{stock_code}/basic'
    
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#     }
    
#     try:
#         api_response = requests.get(api_url, headers=headers)
#         if api_response.status_code == 200:
#             stock_basic_data = api_response.json()
#             return stock_basic_data
#         else:
#             return {}
#     except Exception as e:
#         print(f"Error fetching API data: {e}")
#         return {}

# # 비교할 주식 코드
# stock_code = "005930"  # 예: 삼성전자

# # 웹 페이지 스크래핑 시간 측정
# start_time = time.time()
# fetch_stock_info_quant(stock_code)
# end_time = time.time()
# print(f"Web scraping execution time: {end_time - start_time:.4f} seconds")

# # API 호출 시간 측정
# start_time = time.time()
# fetch_stock_info_quant_API(stock_code)
# end_time = time.time()
# print(f"API call execution time: {end_time - start_time:.4f} seconds")

# import requests
# from datetime import datetime

# def fetch_stock_info_quant_API(stock_code):
#     # API URL 설정
#     api_url = f'https://m.stock.naver.com/api/stock/{stock_code}/finance/annual'
    
#     # API 호출 및 데이터 가져오기
#     try:
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
#         }
#         api_response = requests.get(api_url, headers=headers)
        
#         if api_response.status_code != 200:
#             print(f"Failed to fetch API data: Status code {api_response.status_code}")
#             return
        
#         stock_finance_data = api_response.json()
    
#     except Exception as e:
#         print(f"Error fetching API data: {e}")
#         return
    
#     # 현재 연도 계산
#     current_year = datetime.now().year

#     # 현재 연도와 일치하는 키값 찾기
#     available_keys = [key['key'] for key in stock_finance_data['financeInfo']['trTitleList'] if key['key'][:4] == str(current_year)]

#     # 키값이 없을 경우 "N/A" 처리
#     if not available_keys:
#         target_key = None
#     else:
#         # 가장 최근 연도의 키값 선택
#         target_key = max(available_keys)

#     # 예상 ROE와 주당배당금 추출
#     try:
#         roe = next(item for item in stock_finance_data['financeInfo']['rowList'] if item['title'] == 'ROE')
#         dividend = next(item for item in stock_finance_data['financeInfo']['rowList'] if item['title'] == '주당배당금')

#         # 해당 연도의 데이터 출력
#         if target_key and target_key in roe['columns'] and target_key in dividend['columns']:
#             expected_roe = roe['columns'][target_key]['value']
#             expected_dividend = dividend['columns'][target_key]['value']
#         else:
#             expected_roe = "N/A"
#             expected_dividend = "N/A"
        
#         print(f"{current_year}년 예상 ROE: {expected_roe}")
#         print(f"{current_year}년 예상 주당배당금: {expected_dividend}")
    
#     except Exception as e:
#         print(f"Error processing stock data: {e}")
#         return

# # 함수 호출 예시 (삼성전자 종목 코드: 005930)
# fetch_stock_info_quant_API('005930')
