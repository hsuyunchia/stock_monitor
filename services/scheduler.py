from datetime import datetime
import zoneinfo
from collections import defaultdict
from sqlmodel import Session, select
from apscheduler.schedulers.background import BackgroundScheduler
from database import engine
from models import User, UserSchedule, Watchlist, StockMeta
from services.fetcher import fetch_current_prices
from services.notifier import send_summary_email

def check_and_notify():
    # 1. Force Taipei Timezone
    tz = zoneinfo.ZoneInfo("Asia/Taipei")
    now = datetime.now(tz)
    current_time_str = now.strftime("%H:%M") # "15:45"
    is_weekend = now.weekday() >= 5
    
    print(f"\n--- 🚀 SCHEDULER WOKE UP AT: {current_time_str} ---")
    
    with Session(engine) as session:
        # ----- DEBUG: Print all schedules in the database -----
        all_schedules = session.exec(select(UserSchedule)).all()
        print(f"👀 DB Dump (All Schedules): {[(s.check_time, s.frequency, s.user_id) for s in all_schedules]}")
        
        # 2. Search for matching schedules
        freqs = ["everyday", "weekend" if is_weekend else "weekday"]
        
        # THE FIX: Use .startswith() in case the DB saved "15:45:00"
        statement = select(UserSchedule).where(
            UserSchedule.check_time.startswith(current_time_str), 
            UserSchedule.frequency.in_(freqs)
        )
        schedules = session.exec(statement).all()
        
        if not schedules:
            print(f"🛑 ABORT: No schedules matched '{current_time_str}' with frequencies {freqs}.")
            return
            
        user_ids = list(set([s.user_id for s in schedules]))
        print(f"✅ PASS: Found matching schedules for User IDs: {user_ids}")
        
        # 3. Search for active watchlists
        results = session.exec(
            select(Watchlist, StockMeta)
            .join(StockMeta, Watchlist.symbol == StockMeta.symbol)
            .where(Watchlist.user_id.in_(user_ids), Watchlist.is_active == True)
        ).all()
        
        if not results:
            print(f"🛑 ABORT: User {user_ids} has NO active watchlists.")
            return
            
        print(f"✅ PASS: Found {len(results)} active watchlists. Fetching prices now...")
        
        # 4. Fetch Prices
        unique_symbols = {r[0].symbol for r in results}
        current_prices = fetch_current_prices(list(unique_symbols))
        print(f"📈 API Result: {current_prices}")
        
        # 5. Evaluate Conditions
        hits_by_user = defaultdict(list)
        for watchlist_item, meta_item in results:
            price = current_prices.get(watchlist_item.symbol)
            if price is None: 
                print(f"⚠️ Missing price for {watchlist_item.symbol}")
                continue
            
            is_hit = False
            if watchlist_item.condition == 'gte' and price >= watchlist_item.target_price: is_hit = True
            if watchlist_item.condition == 'lte' and price <= watchlist_item.target_price: is_hit = True
            
            if is_hit:
                print(f"🎯 HIT! {watchlist_item.symbol} current ({price}) vs target ({watchlist_item.condition} {watchlist_item.target_price})")
                hits_by_user[watchlist_item.user_id].append({
                    "symbol": watchlist_item.symbol,
                    "name": meta_item.name,
                    "current_price": price,
                    "target_price": watchlist_item.target_price,
                    "condition": watchlist_item.condition
                })
            else:
                print(f"💤 No Hit: {watchlist_item.symbol} current ({price}) vs target ({watchlist_item.condition} {watchlist_item.target_price})")

        # 6. Send Emails
        for uid, alerts in hits_by_user.items():
            user = session.get(User, uid)
            if user:
                print(f"📧 Sending email to User {uid} ({user.email})...")
                send_summary_email(user.email, alerts)

def start_scheduler():
    scheduler = BackgroundScheduler()
    # TEMPORARY QA MODE: Run every minute! (Change back to '0,15,30,45' later)
    scheduler.add_job(check_and_notify, 'cron', minute='0,15,30,45')
    scheduler.start()