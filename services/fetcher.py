import yfinance as yf
import logging

logger = logging.getLogger("uvicorn")

def fetch_current_prices(symbols: list) -> dict:
    if not symbols: return {}
    prices = {}
    
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            
            # 【關鍵修改】: 抓取過去 1 個月的歷史資料，確保無懼任何長假或休市
            historical_data = ticker.history(period="1mo")
            
            if not historical_data.empty:
                # .iloc[-1] 代表抓取 DataFrame 的最後一列 (最新的一天)
                # 取出那一天的 'Close' (收盤價)
                price = historical_data['Close'].iloc[-1]
                
                prices[symbol] = round(float(price), 2)
                print(f"✅ API 抓取成功: {symbol} = {prices[symbol]}")
            else:
                # 只有在過去一個月「完全沒有」交易紀錄時才會觸發
                print(f"⚠️ API 回傳空資料，可能該股票已下市或代號錯誤: {symbol}")
                
        except Exception as e:
            print(f"❌ API 抓取失敗 {symbol}: {e}")
            
    return prices

def get_stock_meta(symbol: str) -> dict:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        # 優先順序: longName > shortName > symbol
        name = info.get('longName') or info.get('shortName') or symbol
        return {
            "symbol": symbol.upper(),
            "name": name,
            "currency": info.get('currency', 'USD')
        }
    except:
        return None