import requests
import re
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
        # 현재주가 
        current_price = soup.select_one('#middle > dl > dd:nth-child(5)').get_text(strip=True)
        match = re.search(r'현재가 ([\d,]+) 전일대비', current_price)

        # 변수 정의 및 값 추출
        if match:
            current_price = match.group(1)  # 찾은 값
            current_price = int(current_price.replace(',', ''))  # 쉼표 제거
            print(f'현재가: {current_price}')
        else:
            current_price = 'N/A'
            print('현재가를 찾을 수 없습니다.')

        # PER
        per_value = info_section.select_one('tr:nth-of-type(1) > td')
        if per_value:
            data['PER'] = per_value.get_text(strip=True).split('l')[0].split('배')[0]
        else:
            data['PER'] = 'N/A'
            print("PER 값을 찾을 수 없습니다.")  # 로그: PER 없음

        # 추정PER
        # FWD EPS와 현재 주식 가격을 이용한 FWD PER 계산
        est_eps_value = soup.select_one('#_cns_eps')
        if est_eps_value:
            est_eps_text = est_eps_value.get_text(strip=True).split('|')[0]
            # print('est_eps_text',est_eps_text)
            try:
                est_eps_value = float(est_eps_text.replace(',', ''))  # 쉼표 제거 및 부동 소수점으로 변환
                if current_price > 0:  # 현재 주식 가격이 0보다 커야 나누기가 가능함
                    # print('est_eps_value', est_eps_value)
                    fwd_per = round(current_price/est_eps_value, 2)
                    data['fwdPER'] = fwd_per
                else:
                    data['fwdPER'] = 'N/A'
                    print("현재 주식 가격이 유효하지 않습니다.")
            except ValueError:
                data['fwdPER'] = 'N/A'
                print("FWD EPS 값이 유효하지 않습니다.")
        else:
            data['fwdPER'] = 'N/A'
            print("FWD EPS 값을 찾을 수 없습니다.")

        # PBR
        pbr_value = info_section.select_one('tr:nth-of-type(2) > td')
        if pbr_value:
            data['PBR'] = pbr_value.get_text(strip=True).split('l')[0].split('배')[0]
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

        # 예상 배당수익률(정산)
        # 예상 배당수익금
        est_dividend_price_value_text = soup.select_one('#content > div.section.cop_analysis > div.sub_section > table > tbody > tr:nth-child(14) > td.t_line.cell_strong')
        if est_dividend_price_value_text:
            est_dividend_price_value_text = est_dividend_price_value_text.get_text(strip=True).split('%')[0]
            est_dividend_price_value_text = est_dividend_price_value_text.replace(',', '')
            try:
                est_dividend_price_value = int(est_dividend_price_value_text)
            except ValueError:
                est_dividend_price_value = None
        else:
            est_dividend_price_value = None


        print('current_price', current_price)
        print('est_dividend_price_value', est_dividend_price_value)
        if current_price is not None and est_dividend_price_value is not None and est_dividend_price_value != 0:
            est_dividend_yield_value = est_dividend_price_value / current_price * 100
            est_dividend_yield_value = round(est_dividend_yield_value, 2)
        else:
            est_dividend_yield_value = 'N/A'

        if est_dividend_yield_value:
            data['예상배당수익률'] = est_dividend_yield_value
        else:
            data['예상배당수익률'] = 'N/A'
            print("예상배당수익률 값을 찾을 수 없습니다.")  # 로그: 예상 배당수익률 없음

        # ROE 정보 추출
        roe_tag = soup.select_one('#content > div.section.cop_analysis > div.sub_section > table > tbody > tr:nth-child(6) > td.t_line.cell_strong')
        if roe_tag:
            data['ROE'] = roe_tag.get_text(strip=True).replace('\n', 'N/A').replace('\xa0', 'N/A').strip()
        else:
            data['ROE'] = 'N/A'
            print("ROE 정보를 찾을 수 없습니다.")  # 로그: ROE 정보 없음

    except Exception as e:
        print(f"Error parsing data: {e}")  # 로그: 파싱 오류

    for key in data:
        if data[key] == '':
            data[key] = 'N/A'

    # 결과 출력
    print(f"종목명: {data.get('종목명', 'N/A')}")
    print(f"PER: {data.get('PER', 'N/A')}배")
    print(f"fwdPER: {data.get('fwdPER', 'N/A')}배")
    print(f"PBR: {data.get('PBR', 'N/A')}배")
    print(f"ROE: {data.get('ROE', 'N/A')}%")
    print(f"(작년)배당수익률: {data.get('배당수익률', 'N/A')}%")
    print(f"(fwd)배당수익률: {data.get('예상배당수익률', 'N/A')}%")
    
# 예시: 기아의 코드 000270
fetch_stock_info('316140')
