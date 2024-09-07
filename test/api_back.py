import requests
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

    # API에서 가져온 데이터로 딕셔너리 생성
    data = {
        '종목명': api_data.get('stockName', 'N/A'),
        '현재가': api_data.get('currentPrice', 'N/A'),
        '전일비': api_data.get('changeAmount', 'N/A'),
        '등락률': api_data.get('changeRate', 'N/A'),
        'PER': api_data.get('PER', 'N/A'),
        'fwdPER': api_data.get('fwdPER', 'N/A'),
        'PBR': api_data.get('PBR', 'N/A'),
        '배당수익률': api_data.get('dividendYield', 'N/A'),
        '예상배당수익률': api_data.get('estimatedDividendYield', 'N/A'),
        'ROE': api_data.get('ROE', 'N/A'),
        '1D': api_data.get('yield1D', 'N/A'),
        '1W': api_data.get('yield1W', 'N/A'),
        '1M': api_data.get('yield1M', 'N/A'),
        '3M': api_data.get('yield3M', 'N/A'),
        '6M': api_data.get('yield6M', 'N/A'),
        'YTD': api_data.get('yieldYTD', 'N/A'),
        '1Y': api_data.get('yield1Y', 'N/A'),
        '비고(메모)': api_data.get('memo', ' '),
        '종목코드': stock_code,
        '네이버url': f'https://finance.naver.com/item/main.naver?code={stock_code}'
    }

    # 숫자로 변환할 수 있는 항목들을 float으로 변환
    numeric_keys = ['PER', 'fwdPER', 'PBR', '배당수익률', 'ROE', '현재가', '전일비', '등락률', '1D', '1W', '1M', '3M', '6M', 'YTD', '1Y']

    for key in numeric_keys:
        if key in data and isinstance(data[key], str):
            # 문자열에서 ','와 '%' 제거 후 float으로 변환
            value = data[key].replace(',', '').replace('%', '')
            try:
                data[key] = float(value)
            except ValueError:
                data[key] = 'N/A'  # 변환할 수 없는 경우 'N/A'로 처리

    # 순서 지정된 컬럼 순서에 맞게 데이터 정렬
    ordered_data = {
        '종목명': data.get('종목명', 'N/A'),
        'PER': data.get('PER', 'N/A'),
        'fwdPER': data.get('fwdPER', 'N/A'),
        'PBR': data.get('PBR', 'N/A'),
        '배당수익률': data.get('배당수익률', 'N/A'),
        '예상배당수익률': data.get('예상배당수익률', 'N/A'),
        'ROE': data.get('ROE', 'N/A'),
        '현재가': data.get('현재가', 'N/A'),
        '전일비': data.get('전일비', 'N/A'),
        '등락률': data.get('등락률', 'N/A'),
        '비고(메모)': data.get('비고(메모)', ' '),
        '1D': data.get('1D', 'N/A'),
        '1W': data.get('1W', 'N/A'),
        '1M': data.get('1M', 'N/A'),
        '3M': data.get('3M', 'N/A'),
        '6M': data.get('6M', 'N/A'),
        'YTD': data.get('YTD', 'N/A'),
        '1Y': data.get('1Y', 'N/A'),
        '종목코드': data.get('종목코드', 'N/A'),
        '네이버url': data.get('네이버url', 'N/A'),
    }

    print(ordered_data)

    return ordered_data

# 사용 예
fetch_stock_info_quant('005930')
