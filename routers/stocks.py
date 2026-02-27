from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse # Ensure this is imported
from sqlmodel import Session, select
from database import get_session
from models import Watchlist, StockMeta
from services.fetcher import get_stock_meta

router = APIRouter(prefix="/stocks", tags=["stocks"])

@router.post("/add")
def add_stock(
    user_id: int = Form(...), symbol: str = Form(...), 
    target_price: float = Form(...), condition: str = Form(...),
    session: Session = Depends(get_session)
):
    clean_symbol = symbol.upper().strip()
    
    # 1. Check Meta
    if not session.get(StockMeta, clean_symbol):
        meta = get_stock_meta(clean_symbol)
        if not meta: 
            return RedirectResponse(url="/", status_code=303) # Fails silently back to home
        session.add(StockMeta(**meta))
        session.commit()
    
    # 2. CHECK FOR DUPLICATES (The Fix)
    existing_rule = session.exec(
        select(Watchlist).where(
            Watchlist.user_id == user_id,
            Watchlist.symbol == clean_symbol,
            Watchlist.target_price == target_price,
            Watchlist.condition == condition
        )
    ).first()
    
    # 3. Add New Rule ONLY if it doesn't exist
    if not existing_rule:
        new_watch = Watchlist(
            user_id=user_id, symbol=clean_symbol, 
            target_price=target_price, condition=condition
        )
        session.add(new_watch)
        session.commit()
        
    return RedirectResponse(url="/", status_code=303)

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

