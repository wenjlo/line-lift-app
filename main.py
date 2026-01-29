import os
import json
from datetime import datetime
from dotenv import load_dotenv
from src.repositories.sheet import get_video_df
from src.repositories.s3 import upload_to_r2
from config import video_sheet_map


load_dotenv()
access_key = os.getenv('R2_ACCESS_KEY')
secret_key = os.getenv('R2_SECRET_KEY')

def sheet_to_json(df):
    all_video = []
    for _,row in df.iterrows():
        video_object = {
            "title":row['標題'],
            "price":row['內容'],
            "address":row['內容'],
            "image_url":row['圖片'],
            "video_m3u8":row['影片'],
            "detail_url":row['連結']
        }
        all_video.append(video_object)
    return all_video

data = get_video_df(video_sheet_map["更新影片"])
data = sheet_to_json(data)
file_name = f"video-{datetime.now().date()}.json"

with open(file_name, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"檔案已成功儲存至: {file_name}")

upload_to_r2("./video-2026-01-29.json",bucket_name="line-lift",object_name=file_name,account_id=os.getenv("ACCOINT_ID"),access_key=access_key,secret_key=secret_key)