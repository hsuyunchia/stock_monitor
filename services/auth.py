import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt

# 建立密碼加密器 (使用 bcrypt 演算法)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 💡 從環境變數讀取金鑰，如果沒有就先用預設的測試金鑰
SECRET_KEY = os.getenv("SECRET_KEY", "my_super_secret_mvp_key_12345")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # Token 預設有效期限：7 天

def verify_password(plain_password, hashed_password):
    """比對使用者輸入的明碼，與資料庫的雜湊密碼是否吻合"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """將使用者的明碼密碼進行 bcrypt 雜湊加密"""
    return pwd_context.hash(password)

def create_access_token(data: dict):
    """核發 JWT 通行證"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # 使用 SECRET_KEY 將資料與過期時間簽名成一組字串 (Token)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt