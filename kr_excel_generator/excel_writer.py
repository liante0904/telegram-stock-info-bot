import pandas as pd

def save_to_excel(market_dfs, df_etf, file_path):
    """엑셀 파일 생성"""
    with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
        if "KOSPI" in market_dfs:
            market_dfs["KOSPI"].to_excel(writer, sheet_name="KOSPI", index=False)
        if "KOSDAQ" in market_dfs:
            market_dfs["KOSDAQ"].to_excel(writer, sheet_name="KOSDAQ", index=False)
        df_etf.to_excel(writer, sheet_name="ETF_ETN", index=False)
        for sheet in writer.sheets.values():
            sheet.set_column(1, 1, 25)
            sheet.freeze_panes(1, 0)
    return file_path
