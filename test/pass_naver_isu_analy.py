import requests
from bs4 import BeautifulSoup

def fetch_stock_info(stock_code):
    # 주식 종목 페이지 URL
    url = f'https://finance.naver.com/item/main.naver?code={stock_code}'
    
    print(f"Fetching data from: {url}")  # 로그: 요청 URL
    
    # HTTP 요청
    response = requests.get(url)
    response.encoding = 'euc-kr'
    
    if response.status_code == 200:
        print("Page successfully fetched.")  # 로그: 요청 성공
    else:
        print(f"Failed to fetch page: Status code {response.status_code}")
        return

    # 페이지 내용 파싱
    soup = BeautifulSoup(response.text, 'html.parser')

    # 종목명 추출
    stock_name_tag = soup.find('div', {'class': 'wrap_company'}).find('h2')
    if stock_name_tag:
        stock_name = stock_name_tag.get_text(strip=True).split(' ')[0]  # 종목명만 추출
        print(f"종목명: {stock_name}")  # 로그: 종목명
    else:
        stock_name = 'N/A'
        print("종목명을 찾을 수 없습니다.")  # 로그: 종목명 없음

    # PER, 추정PER, PBR, 배당수익률 정보를 담고 있는 테이블 찾기
    info_section = soup.select_one('#tab_con1 > div:nth-child(5)')
    if not info_section:
        print("정보 섹션을 찾을 수 없습니다.")
        return

    print("Information section found.")  # 로그: 정보 섹션 찾음

    # 각 항목에 대한 CSS 선택자
    data = {'종목명': stock_name}
    
    try:
        # PER
        per_value = info_section.select_one('tr:nth-of-type(1) > td')
        if per_value:
            data['PER'] = per_value.get_text(strip=True).split(' ')[0].split('배')[0]
        else:
            data['PER'] = 'N/A'
            print("PER 값을 찾을 수 없습니다.")  # 로그: PER 없음

        # 추정PER
        est_per_value = soup.select_one('#_cns_per')
        if est_per_value:
            data['추정PER'] = est_per_value.get_text(strip=True).split('배')[0]
        else:
            data['추정PER'] = 'N/A'
            print("추정PER 값을 찾을 수 없습니다.")  # 로그: 추정PER 없음

        # PBR
        pbr_value = info_section.select_one('tr:nth-of-type(2) > td')
        if pbr_value:
            data['PBR'] = pbr_value.get_text(strip=True).split(' ')[0].split('배')[0]
        else:
            data['PBR'] = 'N/A'
            print("PBR 값을 찾을 수 없습니다.")  # 로그: PBR 없음

        # 배당수익률
        dividend_yield_value = info_section.select_one('#_dvr')
        if dividend_yield_value:
            data['배당수익률'] = dividend_yield_value.get_text(strip=True).split(' ')[0]
        else:
            data['배당수익률'] = 'N/A'
            print("배당수익률 값을 찾을 수 없습니다.")  # 로그: 배당수익률 없음

        # 예상 배당수익률
        current_price = soup.select_one('#content > div.section.cop_analysis > div.sub_section > table > tbody > tr:nth-child(14) > td.t_line.cell_strong').get_text(strip=True).split('%')[0]
        current_price = current_price.replace(',', '')  # 쉼표 제거
        current_price = int(current_price)

        est_dividend_price_value = soup.select_one('#content > div.section.trade_compare > table > tbody > tr:nth-child(1) > td:nth-child(2)').get_text(strip=True).split('%')[0]
        est_dividend_price_value = est_dividend_price_value.replace(',', '')  # 쉼표 제거

        est_dividend_price_value = int(est_dividend_price_value)
        print(est_dividend_price_value)
        est_dividend_yield_value = current_price / est_dividend_price_value * 100
        # 소수점 셋째 자리에서 반올림
        est_dividend_yield_value = round(est_dividend_yield_value, 2)

        if est_dividend_yield_value:
            data['예상배당수익률'] = est_dividend_yield_value
        else:
            data['예상배당수익률'] = 'N/A'
            print("예상배당수익률 값을 찾을 수 없습니다.")  # 로그: 예상 배당수익률 없음

    except Exception as e:
        print(f"Error parsing data: {e}")  # 로그: 파싱 오류

    # ROE 정보 추출
    roe_tag = soup.select_one('#content > div.section.cop_analysis > div.sub_section > table > tbody > tr:nth-child(6) > td.t_line.cell_strong')
    if roe_tag:
        data['ROE'] = roe_tag.get_text(strip=True).replace('\n', ' ').replace('\xa0', ' ').strip()
    else:
        data['ROE'] = 'N/A'
        print("ROE 정보를 찾을 수 없습니다.")  # 로그: ROE 정보 없음

    # 결과 출력
    print(f"종목명: {data.get('종목명', 'N/A')}")
    print(f"PER: {data.get('PER', 'N/A')}배")
    print(f"fwdPER: {data.get('추정PER', 'N/A')}배")
    print(f"PBR: {data.get('PBR', 'N/A')}배")
    print(f"ROE: {data.get('ROE', 'N/A')}%")
    print(f"(작년)배당수익률: {data.get('배당수익률', 'N/A')}%")
    print(f"(fwd)배당수익률: {data.get('예상배당수익률', 'N/A')}%")
    
# 예시: 기아의 코드 000270
fetch_stock_info('000270')
