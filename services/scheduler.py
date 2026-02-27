from datetime import datetime
from collections import defaultdict
from sqlmodel import Session, select
from apscheduler.schedulers.background import BackgroundScheduler
from database import engine
from models import User, UserSchedule, Watchlist, StockMeta
from services.fetcher import fetch_current_prices
from services.notifier import send_summary_email

def check_and_notify():
    now = datetime.now()
    current_time_str = now.strftime("%H:%M")
    is_weekend = now.weekday() >= 5 # 5=Sat, 6=Sun

    print(f"⏰ Scheduler waking up: {current_time_str} (Weekend: {is_weekend})")

    with Session(engine) as session:
        # 1. 篩選使用者
        freqs = ["everyday"]
        freqs.append("weekend" if is_weekend else "weekday")
        
        schedules = session.exec(select(UserSchedule).where(
            UserSchedule.check_time == current_time_str,
            UserSchedule.frequency.in_(freqs)
        )).all()
        
        user_ids = list(set([s.user_id for s in schedules]))
        if not user_ids: return

        # 2. 撈取 Active 的監測單
        # 這裡做 join 是為了待會發信可以直接拿 StockMeta 的名字
        results = session.exec(
            select(Watchlist, StockMeta)
            .join(StockMeta, Watchlist.symbol == StockMeta.symbol)
            .where(Watchlist.user_id.in_(user_ids), Watchlist.is_active == True)
        ).all()
        
        if not results: return

        # 3. 批次爬價
        unique_symbols = {r[0].symbol for r in results}
        current_prices = fetch_current_prices(list(unique_symbols))
        
        # 4. 比對與分組
        hits_by_user = defaultdict(list)
        
        for watchlist_item, meta_item in results:
            price = current_prices.get(watchlist_item.symbol)
            if price is None: continue
            
            is_hit = False
            if watchlist_item.condition == 'gte' and price >= watchlist_item.target_price: is_hit = True
            if watchlist_item.condition == 'lte' and price <= watchlist_item.target_price: is_hit = True
            
            if is_hit:
                hits_by_user[watchlist_item.user_id].append({
                    "symbol": watchlist_item.symbol,
                    "name": meta_item.name,
                    "current_price": price,
                    "target_price": watchlist_item.target_price,
                    "condition": watchlist_item.condition
                })

        # 5. 發送通知
        for uid, alerts in hits_by_user.items():
            user = session.get(User, uid)
            if user:
                send_summary_email(user.email, alerts)

def start_scheduler():
    scheduler = BackgroundScheduler()
    # 每 15 分鐘執行一次 (0, 15, 30, 45)
    scheduler.add_job(check_and_notify, 'cron', minute='0,15,30,45')
    scheduler.start()