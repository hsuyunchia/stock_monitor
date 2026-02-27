import requests
from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse, JSONResponse
from sqlmodel import Session, select
from database import get_session
from models import Watchlist, StockMeta
from services.fetcher import get_stock_meta
import yfinance as yf

router = APIRouter(prefix="/stocks", tags=["stocks"])

# 💡 新增：串接 Yahoo Finance 官方搜尋 API
@router.get("/search")
def search_ticker(q: str):
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={q}&quotesCount=5&newsCount=0"
    headers = {"User-Agent": "Mozilla/5.0"} # Yahoo 需要 User-Agent 才不會擋
    try:
        res = requests.get(url, headers=headers, timeout=3)
        data = res.json()
        # 過濾出有 symbol 的結果，並組合名稱
        results = [
            {"symbol": item['symbol'], "name": item.get('shortname', item.get('longname', ''))} 
            for item in data.get('quotes', []) if 'symbol' in item
        ]
        return results
    except Exception as e:
        return []

@router.post("/add")
def add_stock(
    user_id: int = Form(...), symbol: str = Form(...), 
    target_price: float = Form(...), condition: str = Form(...),
    session: Session = Depends(get_session)
):
    clean_symbol = symbol.upper().strip()
    
    # 💡 終極防線：直接檢查這檔股票有沒有交易紀錄
    try:
        ticker = yf.Ticker(clean_symbol)
        hist = ticker.history(period="1mo") # 抓一個月防連續假日
        if hist.empty:
            return JSONResponse(status_code=400, content={"message": f"找不到代號 {clean_symbol} 的交易紀錄，請確認代號是否正確。"})
    except Exception:
        return JSONResponse(status_code=400, content={"message": f"查詢 {clean_symbol} 失敗，請確認代號是否有效。"})

    # 嚴格阻擋：確保 meta 也有抓到
    meta = get_stock_meta(clean_symbol)
    if not meta or not meta.get('name'): 
        return JSONResponse(status_code=400, content={"message": f"無法獲取 {clean_symbol} 的基本資料。"})
        
    if not session.get(StockMeta, clean_symbol):
        session.add(StockMeta(**meta))
        session.commit()

    # 檢查重複
    existing_rule = session.exec(
        select(Watchlist).where(
            Watchlist.user_id == user_id,
            Watchlist.symbol == clean_symbol,
            Watchlist.target_price == target_price,
            Watchlist.condition == condition
        )
    ).first()
    
    if existing_rule:
        return JSONResponse(status_code=400, content={"message": "這組監測條件已經存在清單中了喔！"})
        
    # 新增寫入
    new_watch = Watchlist(user_id=user_id, symbol=clean_symbol, target_price=target_price, condition=condition)
    session.add(new_watch)
    session.commit()
    
    return JSONResponse(status_code=200, content={"message": "新增成功！"})

@router.post("/delete/{item_id}") # 為了方便 HTML Form 使用 POST
def delete_stock(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Watchlist, item_id)
    if item:
        session.delete(item)
        session.commit()
    return RedirectResponse(url="/", status_code=303)

@router.post("/toggle/{item_id}")
def toggle_active(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Watchlist, item_id)
    if item:
        item.is_active = not item.is_active
        session.add(item)
        session.commit()
    return RedirectResponse(url="/", status_code=303)

