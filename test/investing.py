import subprocess

# curl 명령어
curl_command = [
    'curl', 
    # 다우
    # 'https://api.investing.com/api/financialdata/assets/equitiesByIndices/169?fields-list=id%2Cname%2Csymbol%2CisCFD%2Chigh%2Clow%2Clast%2ClastPairDecimal%2Cchange%2CchangePercent%2Cvolume%2Ctime%2CisOpen%2Curl%2Cflag%2CcountryNameTranslated%2CexchangeId%2CperformanceDay%2CperformanceWeek%2CperformanceMonth%2CperformanceYtd%2CperformanceYear%2Cperformance3Year%2CtechnicalHour%2CtechnicalDay%2CtechnicalWeek%2CtechnicalMonth%2CavgVolume%2CfundamentalMarketCap%2CfundamentalRevenue%2CfundamentalRatio%2CfundamentalBeta%2CpairType&country-id=&filter-domain=&page=0&page-size=0&limit=0&include-additional-indices=false&include-major-indices=false&include-other-indices=false&include-primary-sectors=false&include-market-overview=false',
    # 나스닥100
    # 'https://api.investing.com/api/financialdata/assets/equitiesByIndices/20?fields-list=id%2Cname%2Csymbol%2Chigh%2Clow%2Clast%2ClastPairDecimal%2Cchange%2CchangePercent%2Cvolume%2Ctime%2CisOpen%2Curl%2Cflag%2CcountryNameTranslated%2CexchangeId%2CperformanceDay%2CperformanceWeek%2CperformanceMonth%2CperformanceYtd%2CperformanceYear%2Cperformance3Year%2CavgVolume%2CfundamentalMarketCap%2CfundamentalRevenue%2CfundamentalRatio%2CfundamentalBeta%2CpairType&country-id=&filter-domain=&page=0&page-size=0&limit=0&include-additional-indices=false&include-major-indices=false&include-other-indices=false&include-primary-sectors=false&include-market-overview=false',
    # S&P500
    'https://api.investing.com/api/financialdata/assets/equitiesByIndices/166?fields-list=id%2Cname%2Csymbol%2Chigh%2Clow%2Clast%2ClastPairDecimal%2Cchange%2CchangePercent%2Cvolume%2Ctime%2CisOpen%2Curl%2Cflag%2CcountryNameTranslated%2CexchangeId%2CperformanceDay%2CperformanceWeek%2CperformanceMonth%2CperformanceYtd%2CperformanceYear%2Cperformance3Year%2CavgVolume%2CfundamentalMarketCap%2CfundamentalRevenue%2CfundamentalRatio%2CfundamentalBeta%2CpairType&country-id=&filter-domain=&page=0&page-size=0&limit=0&include-additional-indices=false&include-major-indices=false&include-other-indices=false&include-primary-sectors=false&include-market-overview=false',
    '-H', 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    '-H', 'accept-language: ko,en-US;q=0.9,en;q=0.8',
    '-H', 'cache-control: no-cache',
    '-H', 'pragma: no-cache',
    '-H', 'priority: u=0, i',
    '-H', 'sec-ch-ua: "Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    '-H', 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
]

# curl 명령어 실행
result = subprocess.run(curl_command, capture_output=True, text=True)

# 결과 출력
if result.returncode == 0:
    print("성공:", result.stdout)
else:
    print(f"오류 발생: {result.returncode}, {result.stderr}")
