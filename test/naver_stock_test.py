# 다른 파일에서 import하여 사용
from naver_stock import naver

if __name__ == "__main__":

    # Report 관련 함수 호출
    naver.report.funcReport()  # 출력: This is funcReport from Report class

    # Stock 관련 함수 호출
    naver.stock.funcStock()    # 출력: This is funcStock from Stock class
    