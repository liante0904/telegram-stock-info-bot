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

CHART_DIR = "chart"

def format_market_cap(value):
    return value / 1e13  # 시가총액을 조 단위로 변환

def calculate_sikige(data):
    # 시기외12 및 시기외26 계산
    data['시기외12'] = 0.0
    data['시기외26'] = 0.0

    for i in range(len(data)):
        if i == 0:
            data.at[data.index[i], '시기외12'] = data.at[data.index[i], '수급오실레이터']
            data.at[data.index[i], '시기외26'] = data.at[data.index[i], '수급오실레이터']
        else:
            data.at[data.index[i], '시기외12'] = data.at[data.index[i], '수급오실레이터'] * 0.1538 + data.at[data.index[i-1], '시기외12'] * (1 - 0.1538)
            data.at[data.index[i], '시기외26'] = data.at[data.index[i], '수급오실레이터'] * 0.0741 + data.at[data.index[i-1], '시기외26'] * (1 - 0.0741)

    return data

def calculate_macd_signal_oscillator(data):
    # MACD 계산
    data['MACD'] = data['시기외12'] - data['시기외26']
    
    # 시그널 계산
    data['시그널'] = 0.0
    for i in range(len(data)):
        if i == 0:
            data.at[data.index[i], '시그널'] = data.at[data.index[i], 'MACD']
        else:
            data.at[data.index[i], '시그널'] = data.at[data.index[i], 'MACD'] * 0.2 + data.at[data.index[i-1], '시그널'] * (1 - 0.2)

    # 오실레이터 값 계산
    data['Oscillator'] = data['MACD'] - data['시그널']

    return data

def draw_chart(stock_code, stock_name):
    if not os.path.exists(CHART_DIR):
        os.makedirs(CHART_DIR)
        
    now = datetime.now()
    if now.hour < 18:
        end_date = (now - timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        end_date = now.strftime('%Y-%m-%d')
    start_date = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=120)).strftime('%Y-%m-%d')

    trading_value = stock.get_market_trading_value_by_date(start_date, end_date, stock_code, on='매수')
    
    # 기관과 외국인의 매수 금액 5일 합 계산
    trading_value['외국인_매수_5일합'] = trading_value['외국인합계'].rolling(window=5).sum()
    trading_value['기관_매수_5일합'] = trading_value['기관합계'].rolling(window=5).sum()

    data = pd.DataFrame({
        '외국인_매수_5일합': trading_value['외국인_매수_5일합'],
        '기관_매수_5일합': trading_value['기관_매수_5일합']
    })
    data = data.dropna()

    market_cap = stock.get_market_cap_by_date(start_date, end_date, stock_code)
    data = data.join(market_cap[['시가총액']], how='inner')

    # 시가총액 데이터 보정 (단위: 조원)
    data['시가총액'] = data['시가총액'].apply(format_market_cap)

    # 수급 오실레이터 %를 시가총액으로 보정
    data['수급오실레이터'] = (data['외국인_매수_5일합'] + data['기관_매수_5일합']) / (data['시가총액'] * 1e13) * 100
    data = data.dropna()

    # 시기외12 및 시기외26 계산
    data = calculate_sikige(data)

    # MACD, 시그널 및 오실레이터 값 계산
    data = calculate_macd_signal_oscillator(data)

    # 시가총액과 오실레이터 차트 생성
    fig, ax1 = plt.subplots(figsize=(14, 7))
    color = 'tab:blue'
    ax1.set_xlabel('날짜')
    ax1.set_ylabel('시가총액 (조원)', color=color)
    ax1.plot(data.index, data['시가총액'], label=f'{stock_name} 시가총액', color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_ylim([data['시가총액'].min() * 0.95, data['시가총액'].max() * 1.05])

    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('오실레이터 (%)', color=color)
    ax2.plot(data.index, data['Oscillator'], label='Oscillator', color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    osc_min = data['Oscillator'].min()
    osc_max = data['Oscillator'].max()
    osc_range = osc_max - osc_min
    ax2.set_ylim([osc_min - osc_range * 0.1, osc_max + osc_range * 0.1])
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.2f}%'))

    # X축 눈금을 7일 간격으로 설정
    ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()

    # X축 마지막 일자 항상 표시
    ax1.set_xticks(list(ax1.get_xticks()) + [mdates.date2num(data.index[-1])])
    ax1.set_xticklabels([item.get_text() if i != len(ax1.get_xticks()) - 1 else data.index[-1].strftime('%Y-%m-%d') for i, item in enumerate(ax1.get_xticklabels())])

    plt.title(f'{stock_name} 시가총액과 오실레이터', fontsize=24, pad=40)  # 글씨 크기를 24포인트로 설정하고 아래로 40포인트 패딩
    fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9))

    fig.tight_layout(rect=[0, 0, 1, 0.95])  # 타이틀 공간 확보를 위해 rect 조정

    # 마지막 데이터 날짜로 파일명 생성
    last_date = data.index[-1].strftime('%Y%m%d')
    chart_filename = os.path.join(CHART_DIR, f'{stock_name}_{stock_code}_{last_date}_chart.png')
    fig.savefig(chart_filename, format='png')
    plt.close(fig)
    print(f"Chart saved as: {chart_filename}")

    # 필요한 열만 선택하여 데이터 CSV 파일로 저장
    selected_data = data[['시가총액', 'Oscillator']].copy()
    selected_data.columns = [f'{stock_name} 시가총액', f'{stock_name} 수급오실레이터']
    selected_data[f'{stock_name} 시가총액'] = selected_data[f'{stock_name} 시가총액'].apply(lambda x: f'{x:.4f}')
    selected_data[f'{stock_name} 수급오실레이터'] = selected_data[f'{stock_name} 수급오실레이터'].apply(lambda x: f'{x:.2f}%')
    
    csv_filename = os.path.join(CHART_DIR, f'{stock_name}_{stock_code}_{last_date}_data.csv')
    selected_data.to_csv(csv_filename, index_label='날짜')
    print(f"CSV saved as: {csv_filename}")

    # 데이터 출력
    print(selected_data)

    return chart_filename, csv_filename

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
    trading_value = stock.get_market_trading_value_by_date(start_date, end_date, stock_code, on='매수')
    return trading_value.index[-1].strftime('%Y%m%d')

def main():
    stock_code = '005830'  # 예시: DB손해보험
    stock_name = 'DB손해보험'
    chart_filename, csv_filename = draw_chart(stock_code, stock_name)
    open_image(chart_filename)

if __name__ == '__main__':
    main()
