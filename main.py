from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlmodel import Session, select
from database import create_db_and_tables, get_session
from services.scheduler import start_scheduler
from services.auth import SECRET_KEY, ALGORITHM 
from routers import stocks, schedules, auth
from models import User, Watchlist, UserSchedule, StockMeta
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
import re

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    start_scheduler()
    yield

class SecurityFilterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "POST":
            # 💡 檢查是否為表單格式，避免誤傷其他類型的請求
            content_type = request.headers.get("content-type", "")
            if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
                
                # 1. 讀取並快取 Body
                body = await request.body()
                
                # 2. 為了檢查，將 Body 轉成表單物件
                from starlette.datastructures import FormData
                # 這裡模擬讀取過程而不消耗原本的 request 流
                import urllib.parse
                form_dict = urllib.parse.parse_qs(body.decode())
                
                malicious_pattern = r"(\$\{jndi:|ldap:\/\/|script>|<script)"
                
                for key, values in form_dict.items():
                    for value in values:
                        if re.search(malicious_pattern, value, re.IGNORECASE):
                            return JSONResponse(
                                status_code=400,
                                content={"message": f"檢測到不安全的字元輸入 ({key})"}
                            )
                
                # 3. 💡 關鍵：重寫 request 的 receive 函數，讓後續的 Form(...) 能重新讀取 body
                async def receive():
                    return {"type": "http.request", "body": body}
                request._receive = receive

        response = await call_next(request)
        return response

app = FastAPI(lifespan=lifespan)
app.add_middleware(SecurityFilterMiddleware)
app.include_router(auth.router)
app.include_router(stocks.router)
app.include_router(schedules.router)

templates = Jinja2Templates(directory="templates")

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/")
def dashboard(request: Request, session: Session = Depends(get_session)):
    token_cookie = request.cookies.get("access_token")

    if not token_cookie:
        print("🚩 DEBUG: No cookie found in headers")
        return RedirectResponse(url="/login", status_code=303)

    try:
        # 💡 終極容錯：去掉所有可能的 Bearer 前綴、引號、空白
        token = token_cookie.replace("Bearer ", "").strip().strip('"')
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        print(f"✅ DEBUG: Auth Success - User ID: {user_id}")
        # 💡 根據 ID 抓出使用者資料
        user = session.get(User, user_id)
        if not user:
            raise Exception("User not found")
    except Exception as e:
        print(f"Auth Error: {e}")
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("access_token", path="/")
        return response
        
    # 撈取 Watchlist (加入雙重排序)
    watchlist = session.exec(
        select(Watchlist, StockMeta)
        .join(StockMeta, Watchlist.symbol == StockMeta.symbol)
        .where(Watchlist.user_id == user_id)
        .order_by(Watchlist.symbol, Watchlist.target_price)
    ).all()

    # 撈取 Schedules (加入雙重排序)
    schedules = session.exec(
        select(UserSchedule)
        .where(UserSchedule.user_id == user_id)
        .order_by(UserSchedule.check_time, UserSchedule.frequency)
    ).all()

    # 💡 注意這裡：一定要把 user_id 傳給前端
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "watchlist": watchlist, 
        "schedules": schedules,
        "user_id": user_id,
        "user_email": user.email # 👈 傳送 Email 給前端顯示
    })