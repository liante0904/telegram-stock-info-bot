import requests

def fetch_stock_info_quant(stock_code):
    # API URL 설정
    api_url = f'https://m.stock.naver.com/api/stock/{stock_code}/integration'

    # API 요청
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        api_data = response.json()
    except requests.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return {}

    # 데이터 추출 및 변환
    total_infos = {item['key']: item['value'] for item in api_data.get('totalInfos', [])}
    deal_trend_infos = api_data.get('dealTrendInfos', [])

    # 총정보에서 필요한 데이터 추출
    data = {
        '종목명': api_data.get('stockName', 'N/A'),
        '현재가': total_infos.get('전일', 'N/A').replace(',', ''),
        '시가': total_infos.get('시가', 'N/A').replace(',', ''),
        # '고가': total_infos.get('고가', 'N/A').replace(',', ''),
        # '저가': total_infos.get('저가', 'N/A').replace(',', ''),
        # '거래량': total_infos.get('거래량', 'N/A').replace(',', ''),
        # '대금': total_infos.get('대금', 'N/A').replace(',', ''),
        # '시총': total_infos.get('시총', 'N/A').replace(',', ''),
        # '외인소진율': total_infos.get('외인소진율', 'N/A'),
        # '52주 최고': total_infos.get('52주 최고', 'N/A').replace(',', ''),
        # '52주 최저': total_infos.get('52주 최저', 'N/A').replace(',', ''),
        'PER': total_infos.get('PER', 'N/A').replace('배', ''),
        'EPS': total_infos.get('EPS', 'N/A').replace('원', '').replace(',', ''),
        '추정PER': total_infos.get('추정PER', 'N/A').replace('배', ''),
        '추정EPS': total_infos.get('추정EPS', 'N/A').replace('원', '').replace(',', ''),
        'PBR': total_infos.get('PBR', 'N/A').replace('배', ''),
        'BPS': total_infos.get('BPS', 'N/A').replace('원', '').replace(',', ''),
        '배당수익률': total_infos.get('배당수익률', 'N/A').replace('%', ''),
        # '주당배당금': total_infos.get('주당배당금', 'N/A').replace('원', '').replace(',', ''),
        '종목코드': stock_code,
        '네이버url': f'https://finance.naver.com/item/main.naver?code={stock_code}'
    }

    # 숫자로 변환할 수 있는 항목들을 float으로 변환
    numeric_keys = ['현재가', '시가', '고가', '저가', '거래량', '대금', '시총', '52주 최고', '52주 최저', 'PER', 'EPS', '추정PER', '추정EPS', 'PBR', 'BPS', '배당수익률', '주당배당금']

    for key in numeric_keys:
        if key in data and isinstance(data[key], str):
            # 문자열에서 ','와 '%' 제거 후 float으로 변환
            value = data[key].replace(',', '').replace('%', '')
            try:
                data[key] = float(value)
            except ValueError:
                data[key] = 'N/A'  # 변환할 수 없는 경우 'N/A'로 처리


    # 최종 데이터 출력
    print(data)
    return data

# 사용 예
fetch_stock_info_quant('005930')
