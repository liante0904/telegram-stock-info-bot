import pandas as pd
import matplotlib.pyplot as plt

# CSV 파일 로드
raw_data_df = pd.read_csv('raw_data.csv', encoding='utf-8')

# 날짜 컬럼을 datetime 형식으로 변환
raw_data_df['날짜'] = pd.to_datetime(raw_data_df['날짜'])

# 이동 평균 계산
raw_data_df['시가총액_이동평균'] = raw_data_df['시가총액'].rolling(window=5).mean()

# 시각화
plt.figure(figsize=(14, 7))
plt.plot(raw_data_df['날짜'], raw_data_df['시가총액'], label='시가총액')
plt.plot(raw_data_df['날짜'], raw_data_df['시가총액_이동평균'], label='시가총액 이동평균')
plt.xlabel('날짜')
plt.ylabel('시가총액')
plt.title('시가총액과 5일 이동평균')
plt.legend()
plt.show()