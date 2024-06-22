import matplotlib
matplotlib.use('Agg')  # 이 줄을 추가하여 Agg 백엔드를 사용하도록 설정합니다.
import matplotlib.pyplot as plt
from pykrx import stock
from datetime import datetime, timedelta
import pandas as pd

def draw_chart(stock_code, stock_name):
    now = datetime.now()
    if now.hour < 18:
        end_date = (now - timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        end_date = now.strftime('%Y-%m-%d')
    start_date = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=120)).strftime('%Y-%m-%d')

    trading_value = stock.get_market_trading_value_by_date(start_date, end_date, stock_code)
    trading_value['외국인_순매수_5일합'] = trading_value['외국인합계'].rolling(window=5).sum()
    trading_value['기관_순매수_5일합'] = trading_value['기관합계'].rolling(window=5).sum()

    data = pd.DataFrame({
        '외국인_순매수_5일합': trading_value['외국인_순매수_5일합'],
        '기관_순매수_5일합': trading_value['기관_순매수_5일합']
    })
    data['수급오실레이터'] = (data['외국인_순매수_5일합'] + data['기관_순매수_5일합']) / 1e8
    data = data.dropna()

    market_cap = stock.get_market_cap_by_date(start_date, end_date, stock_code)
    data = data.join(market_cap[['시가총액']], how='inner')

    fig, ax1 = plt.subplots(figsize=(14, 7))
    color = 'tab:blue'
    ax1.set_xlabel('날짜')
    ax1.set_ylabel('시가총액', color=color)
    ax1.plot(data.index, data['시가총액'], label=f'{stock_name} 시가총액', color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_ylim([data['시가총액'].min() * 0.95, data['시가총액'].max() * 1.05])

    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('수급 오실레이터 (%)', color=color)
    ax2.plot(data.index, data['수급오실레이터'], label=f'{stock_name} 수급 오실레이터', color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    osc_min = data['수급오실레이터'].min()
    osc_max = data['수급오실레이터'].max()
    osc_range = osc_max - osc_min
    ax2.set_ylim([osc_min - osc_range * 0.1, osc_max + osc_range * 0.1])
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.2f}%'))

    fig.tight_layout()
    plt.title(f'{stock_name} 시가총액과 수급 오실레이터')
    fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9))

    creation_date = now.strftime('%Y%m%d')
    chart_filename = f'{stock_name}_{stock_code}_{creation_date}_chart.png'
    fig.savefig(chart_filename, format='png')
    plt.close(fig)
    print(f"Chart saved as: {chart_filename}")
    return chart_filename
