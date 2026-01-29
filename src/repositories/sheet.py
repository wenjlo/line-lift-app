import pandas as pd
import ssl
import certifi

ssl._create_default_https_context = ssl._create_unverified_context

def get_video_df(sheet_id: str) -> pd.DataFrame:
    #'1Mvlqi9AQs3UHv0KFYz3lPhCHDP6IxPrJkzdv8efaeKY'
    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'

    try:
        # 1. 讀取 CSV (用 python 引擎避免報錯)
        df = pd.read_csv(url, on_bad_lines='skip', engine='python')

        # 2. 【關鍵】刪除全空的欄位 (axis=1 代表直欄)
        df = df.dropna(how='all', axis=1)

        # 3. 如果連列(橫向)也有很多空的，順便清一下 (axis=0 代表橫列)
        df = df.dropna(how='all', axis=0)
        for c in df.columns:
            df[c] = df[c].apply(lambda x: str(x).strip())
        print(df)
        return df

    except Exception as e:
        print(f"讀取失敗: {e}")
        return pd.DataFrame()


