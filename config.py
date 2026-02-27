import os
from dotenv import load_dotenv

# 載入 .env 檔案裡的設定
load_dotenv()

# 資料庫設定
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./stock_monitor.db")

# Email 設定
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER")      # 從環境變數讀取
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD") # 從環境變數讀取

# 檢查是否有漏設
if not SMTP_USER or not SMTP_PASSWORD:
    raise ValueError("❌ 錯誤: 請在 .env 檔案中設定 SMTP 帳密")