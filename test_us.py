from module.naver_stock_quant import fetch_stock_yield_by_period
from module.naver_stock_util import search_stock_code, search_stock_code_mobileAPI
# from module.naver_upjong_quant  import fetch_stock_info_quant_API

def main():
    # r = search_stock_code_mobileAPI('aapl')
    r = search_stock_code('삼성전자')
    if r:
        # fetch_stock_info_quant_API(reutersCode= , nationCode=)
        print('0===>', r)
    else:
        print('No results found.')

if __name__ == '__main__':
    main()
