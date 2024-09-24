import asyncio
import sys
import os
# 현재 스크립트의 상위 디렉터리를 모듈 경로에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from module.naver_upjong_quant import fetch_upjong_list_API, fetch_stock_info_in_upjong, fetch_stock_info_quant_API

# 동기 함수를 비동기적으로 호출하기 위한 래퍼 함수
async def fetch_quant_data_async(stock_code):
    # 동기 함수를 비동기적으로 실행
    quant_data = await asyncio.to_thread(fetch_stock_info_quant_API, stock_code)
    return stock_code, quant_data

# 20종목씩 나누어 비동기 호출
async def process_stock_info(stock_info):
    tasks = []
    for i in range(0, len(stock_info), 20):
        batch = stock_info[i:i+20]  # 20종목씩 처리
        for 종목명, _, _, _, 종목링크 in batch:
            stock_code = 종목링크.split('=')[-1]
            tasks.append(fetch_quant_data_async(stock_code))

        await asyncio.sleep(0.5)  # 1초 대기 후 다음 요청 처리

        # 비동기로 20종목씩 데이터를 가져옴
        quant_results = await asyncio.gather(*tasks)

        # API 호출 결과 처리
        for stock_code, quant_data in quant_results:
            if quant_data:
                print(f"종목 코드 {stock_code}의 퀀트 데이터가 수집되었습니다.")
            else:
                print(f"종목 코드 {stock_code}에서 데이터 수집 실패")

        tasks.clear()  # 다음 20종목을 위해 태스크 초기화

# 업종 처리 함수
async def process_upjong(upjong_map):
    for 업종명, (등락률, 링크) in upjong_map.items():
        print(f"=================업종명: {업종명}, 등락률: {등락률}=================")
        if 업종명 == '기타':  # ETN & ETF는 건너뛰기
            continue

        stock_info = fetch_stock_info_in_upjong(링크)

        if stock_info:
            await process_stock_info(stock_info)  # 비동기 호출로 종목 정보 처리

# 비동기 작업 실행
if __name__ == '__main__':
    upjong_list = fetch_upjong_list_API('KOR')
    upjong_map = {업종명: (등락률, 링크) for 업종명, 등락률, 링크 in upjong_list}

    # 비동기 작업 실행
    asyncio.run(process_upjong(upjong_map))