import yfinance as yf
import logging

logger = logging.getLogger("uvicorn")

def fetch_current_prices(symbols: list) -> dict:
    if not symbols: return {}
    # 使用字串串接一次查詢多支
    tickers = yf.Tickers(" ".join(symbols))
    prices = {}
    for symbol in symbols:
        try:
            # 嘗試使用 fast_info
            price = tickers.tickers[symbol].fast_info.get('last_price')
            if price:
                prices[symbol] = round(price, 2)
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
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