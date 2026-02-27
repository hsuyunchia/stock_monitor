from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select
from database import create_db_and_tables, get_session
from services.scheduler import start_scheduler
from routers import stocks, schedules
from models import User, Watchlist, UserSchedule, StockMeta

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    start_scheduler()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(stocks.router)
app.include_router(schedules.router)

templates = Jinja2Templates(directory="templates")

# --- 簡單的前端頁面路由 ---

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, user_id: int = 1, session: Session = Depends(get_session)):
    # 為了 MVP，這裡預設 user_id=1。實際應做 Login。
    # 請先手動在 DB 建立一個 User (id=1)
    
    # 檢查是否需要自動建立 Demo User
    user = session.get(User, user_id)
    if not user:
        user = User(id=1, email="demo@example.com", password="demo")
        session.add(user)
        session.commit()

    # 1. 取得監測清單
    watchlist = session.exec(
        select(Watchlist, StockMeta)
        .join(StockMeta, Watchlist.symbol == StockMeta.symbol)
        .where(Watchlist.user_id == user_id)
    ).all()

    # 2. 取得排程設定
    schedules = session.exec(select(UserSchedule).where(UserSchedule.user_id == user_id)).all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "user": user,
        "watchlist": watchlist,
        "schedules": schedules
    })