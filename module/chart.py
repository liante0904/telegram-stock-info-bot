import matplotlib
matplotlib.use('Agg')  # 이 줄을 추가하여 Agg 백엔드를 사용하도록 설정합니다.
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pykrx import stock
from datetime import datetime, timedelta
import pandas as pd
import os
import subprocess
import platform

CHART_DIR = "chart/"

# 변환 및 반올림 함수
def convert_and_round(value):
    return round(value / 1e9, 3)  # 10억 단위로 변환 및 반올림

def draw_chart(stock_code, stock_name):
    if not os.path.exists(CHART_DIR):
        os.makedirs(CHART_DIR)
    
    now = datetime.now()
    if now.hour < 18:
        end_date = (now - timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        end_date = now.strftime('%Y-%m-%d')
    start_date = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=120)).strftime('%Y-%m-%d')
    
    trading_value = stock.get_market_trading_value_by_date(start_date, end_date, stock_code, on='순매수')
    
    # 기관과 외국인의 순매수 금액 5일 합 계산
    trading_value['외국인_순매수_5일합'] = trading_value['외국인합계'].rolling(window=5).sum()
    trading_value['기관_순매수_5일합'] = trading_value['기관합계'].rolling(window=5).sum()

    # 억 원 단위로 변환 및 반올림 처리
    trading_value['외국인_순매수_5일합'] = trading_value['외국인_순매수_5일합'].apply(convert_and_round)
    trading_value['기관_순매수_5일합'] = trading_value['기관_순매수_5일합'].apply(convert_and_round)

    data = pd.DataFrame({
        '외국인_순매수_5일합': trading_value['외국인_순매수_5일합'],
        '기관_순매수_5일합': trading_value['기관_순매수_5일합']
    })
    data = data.dropna()

    market_cap = stock.get_market_cap_by_date(start_date, end_date, stock_code)
    market_cap['시가총액'] = (market_cap['시가총액'] / 10**9).round(2)  # 10억 단위로 변환 및 반올림

    data = data.join(market_cap[['시가총액']], how='inner')

    # 수급 오실레이터 %를 시가총액으로 보정
    data['수급오실레이터'] = (data['외국인_순매수_5일합'] + data['기관_순매수_5일합']) / (2 / 13)

    # 시가총액 오실레이터 계산
    data['시가총액 오실레이터'] = (market_cap['시가총액'] / 10000).round(2)  # 시가총액 오실레이터 계산
    data = data.dropna()

    # 시기외 데이터 계산: 기관 및 외국인 순매수 합을 시가총액으로 나눈 값
    data['시기외'] = ((data['기관_순매수_5일합'] + data['외국인_순매수_5일합'])) / data['시가총액']
    
    # 첫 번째 레코드는 시기외의 첫 번째 값으로 초기화
    if not data.empty:  # 데이터프레임이 비어 있지 않은 경우에만 진행
        data.loc[data.index[0], '시기외12'] = data.loc[data.index[0], '시기외']
        data.loc[data.index[0], '시기외26'] = data.loc[data.index[0], '시기외']

        # 나머지 레코드 계산
        for i in range(1, len(data)):
            data.loc[data.index[i], '시기외12'] = data.loc[data.index[i], '시기외'] * 0.1538 + data.loc[data.index[i - 1], '시기외12'] * (1 - 0.1538)
            data.loc[data.index[i], '시기외26'] = data.loc[data.index[i], '시기외'] * 0.0741 + data.loc[data.index[i - 1], '시기외26'] * (1 - 0.0741)

        # MACD 계산: 시기외12와 시기외26의 차이
        data['macd'] = data['시기외12'] - data['시기외26']
        
        # 시그널 계산
        data['시그널'] = 0.0  # 초기화
        data.loc[data.index[0], '시그널'] = data.loc[data.index[0], 'macd']  # 첫 번째 레코드

        # 두 번째 레코드부터 이후 레코드 계산
        for i in range(1, len(data)):
            data.loc[data.index[i], '시그널'] = data.loc[data.index[i], 'macd'] * 0.2 + data.loc[data.index[i - 1], '시그널'] * (1 - 0.2)

        # 수급오실레이터 계산: macd와 시그널의 차이
        data['수급오실레이터'] = ((data['macd'] - data['시그널']) * 100).round(3)

    print(data)

    # Save CSV
    csv_filename = os.path.join(CHART_DIR, f'{stock_name}_{stock_code}_data.csv')
    data[['시가총액 오실레이터', '수급오실레이터']].to_csv(csv_filename, encoding='utf-8-sig')
    print(f"Data saved as: {csv_filename}")

    # Plotting
    fig, ax1 = plt.subplots(figsize=(10, 8))
    
    # Market Cap Oscillator
    ax1.set_xlabel('날짜')
    ax1.set_ylabel('시가총액 (억원)', color='tab:blue')
    ax1.plot(data.index, data['시가총액 오실레이터'], label=f'{stock_name} 시가총액 오실레이터', color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.axhline(0, color='gray', linestyle='--')  # Baseline
    ax1.set_ylim(data['시가총액 오실레이터'].min() * 1.1, data['시가총액 오실레이터'].max() * 1.1)

    # Supply-Demand Oscillator
    ax2 = ax1.twinx()
    ax2.set_ylabel('수급 오실레이터 (%)', color='tab:red')
    ax2.plot(data.index, data['수급오실레이터'], label=f'{stock_name} 수급 오실레이터', color='tab:red')
    ax2.tick_params(axis='y', labelcolor='tab:red')
    ax2.axhline(0, color='gray', linestyle='--')  # Baseline
    ax2.set_ylim(data['수급오실레이터'].min() * 1.1, data['수급오실레이터'].max() * 1.1)

    # X-axis formatting
    ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()

    plt.title(f'{stock_name} 시가총액 오실레이터과 수급 오실레이터(순매수금액기준)', fontsize=24, pad=40)
    fig.tight_layout(rect=[0, 0, 1, 0.95])

    # Save chart
    last_date = data.index[-1].strftime('%Y%m%d')
    chart_filename = os.path.join(CHART_DIR, f'{stock_name}_{stock_code}_{last_date}_chart.png')
    fig.savefig(chart_filename, format='png', bbox_inches='tight')
    plt.close(fig)
    print(f"Chart saved as: {chart_filename}")

    return chart_filename

def open_image(image_path):
    if 'WSL' in os.uname().release:
        subprocess.run(['code', image_path])  # WSL 환경에서 VSCode로 열기
    else:
        system = platform.system()
        if system == 'Linux':
            subprocess.run(['xdg-open', image_path])  # Linux
        elif system == 'Windows':
            os.startfile(image_path)  # Windows
        elif system == 'Darwin':
            subprocess.run(['open', image_path])  # macOS

def get_last_date(stock_code):
    now = datetime.now()
    if now.hour < 18:
        end_date = (now - timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        end_date = now.strftime('%Y-%m-%d')
    start_date = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=120)).strftime('%Y-%m-%d')
    trading_value = stock.get_market_trading_value_by_date(start_date, end_date, stock_code, on='순매수')
    return trading_value.index[-1].strftime('%Y%m%d')

def main():
    stock_code = '005930'  # 예시: 삼성전자
    stock_name = '삼성전자'
    chart_filename = draw_chart(stock_code, stock_name)
    open_image(chart_filename)

if __name__ == '__main__':
    main()
