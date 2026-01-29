import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from dotenv import load_dotenv

# 引入原本的模組
# 請確保 src 和 config 資料夾在同一層目錄
try:
    from src.repositories.sheet import get_video_df
    from src.repositories.s3 import upload_to_r2
    from config import video_sheet_map, source_map
except ImportError as e:
    print(f"模組載入失敗: {e}")
    # 為了讓 UI 在沒有這些模組時也能呈現(測試用)，這裡做了簡單的 mock，實際執行請確保檔案存在
    video_sheet_map = {"更新影片": "SheetID_1", "小潔廠商": "SheetID_2", "幸福廠商": "SheetID_3", "商品": "SheetID_4"}
    source_map = {"更新影片": "video", "小潔廠商": "xiaojie", "幸福廠商": "happiness", "商品": "product"}


    # def get_video_df(sheet_id):
    #     return []  # Mock
    #
    #
    # def upload_to_r2(*args, **kwargs):
    #     pass  # Mock

# 載入環境變數
load_dotenv()
access_key = os.getenv('R2_ACCESS_KEY')
secret_key = os.getenv('R2_SECRET_KEY')
account_id = os.getenv("ACCOUNT_ID")  # 注意：你的環境變數拼字可能是 ACCOINT_ID

# LIFF ID 設定
LIFF_BASE_URL = "https://liff.line.me/2009007017-xNQkb1az"


def sheet_to_json(df):
    """將 DataFrame 轉換為特定格式的 JSON List"""
    all_video = []
    # 如果是 Mock 的空 list 直接返回
    if isinstance(df, list): return []

    for _, row in df.iterrows():
        video_object = {
            "title": row['標題'],
            "price":  row['價格'],
            "address": row['內容'],
            "image_url": row['圖片'],
            "video_m3u8": row['影片'],
            "detail_url": row['連結']
        }
        all_video.append(video_object)
    return all_video


def run_process():
    """執行按鈕的邏輯"""
    source_name = combo_source.get()

    if not source_name:
        messagebox.showwarning("警告", "請先選擇一個選項！")
        return

    btn_run.config(state="disabled", text="處理中...")
    root.update()

    try:
        # 1. 取得資料
        print(f"正在讀取: {source_name}...")
        df = get_video_df(video_sheet_map[source_name])

        # 2. 轉換 JSON
        data = sheet_to_json(df)

        # 3. 準備檔名與日期
        today = datetime.now()
        date_str_file = today.strftime("%Y-%m-%d")  # 檔案用: 2026-01-29
        date_str_url = today.strftime("%Y%m%d")  # 網址用: 20260129

        prefix = source_map.get(source_name, "video")
        file_name = f"{prefix}-{date_str_file}.json"

        # 4. 存檔
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"本地存檔成功: {file_name}")

        # 5. 上傳 R2
        # 注意：這裡修正了原本程式碼寫死 "./video-2026-01-29.json" 的問題
        upload_to_r2(
            local_file_path=f"./{file_name}",
            bucket_name="line-lift",
            object_name=file_name,
            account_id=account_id,
            access_key=access_key,
            secret_key=secret_key
        )
        print("上傳 R2 成功")

        # 6. 產生連結
        # 格式: .../player.html?date=20260129&type=video
        final_url = f"{LIFF_BASE_URL}?date={date_str_url}&type={prefix}"

        # 7. 更新 UI 顯示
        entry_url.delete(0, tk.END)
        entry_url.insert(0, final_url)
        lbl_status.config(text=f"成功！已上傳: {file_name}", foreground="green")

    except Exception as e:
        messagebox.showerror("錯誤", f"發生錯誤:\n{str(e)}")
        lbl_status.config(text="執行失敗", foreground="red")
        print(e)
    finally:
        btn_run.config(state="normal", text="取得連結")


def copy_to_clipboard():
    """複製連結功能"""
    url = entry_url.get()
    if url:
        root.clipboard_clear()
        root.clipboard_append(url)
        messagebox.showinfo("提示", "連結已複製到剪貼簿！")


# ================= UI 建置區 =================
root = tk.Tk()
root.title("線上賞屋資料更新器")
root.geometry("500x350")
root.resizable(False, False)

# Style 設定
style = ttk.Style()
style.theme_use('clam')
style.configure('TButton', font=('微軟正黑體', 10))
style.configure('TLabel', font=('微軟正黑體', 11))

# 主框架
main_frame = ttk.Frame(root, padding="20")
main_frame.pack(fill=tk.BOTH, expand=True)

# 標題
ttk.Label(main_frame, text="請選擇更新項目:", font=('微軟正黑體', 12, 'bold')).pack(anchor='w', pady=(0, 5))

# 下拉選單
options = ["更新影片", "小潔廠商", "幸福廠商", "商品"]
combo_source = ttk.Combobox(main_frame, values=options, state="readonly", font=('微軟正黑體', 11))
combo_source.current(0)  # 預設選第一個
combo_source.pack(fill=tk.X, pady=5)

# 執行按鈕
btn_run = ttk.Button(main_frame, text="取得連結 (執行上傳)", command=run_process)
btn_run.pack(fill=tk.X, pady=15, ipady=5)

# 分隔線
ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=10)

# 結果顯示區
ttk.Label(main_frame, text="產生的 LIFF 連結:", font=('微軟正黑體', 10)).pack(anchor='w')

entry_url = ttk.Entry(main_frame, font=('Arial', 10))
entry_url.pack(fill=tk.X, pady=5)

# 複製按鈕
btn_copy = ttk.Button(main_frame, text="複製連結", command=copy_to_clipboard)
btn_copy.pack(fill=tk.X, pady=5)

# 狀態列
lbl_status = ttk.Label(main_frame, text="準備就緒", foreground="gray", font=('微軟正黑體', 9))
lbl_status.pack(side=tk.BOTTOM, pady=10)

# 啟動程式
if __name__ == "__main__":
    root.mainloop()