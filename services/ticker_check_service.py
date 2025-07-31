import yfinance as yf
from numpy import float64
from requests.exceptions import RequestException

def check_symbol(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        if "symbol" not in info or info["symbol"] != symbol:
            return { "symbol": symbol, "valid": False, "current_price": None}
        
        history = ticker.history(period="1d")

        if len(history) > 0 and isinstance(history["Close"].iloc[0], float64):
            return { "symbol": symbol, "valid": True, "current_price": history["Close"].iloc[0]}

        return { "symbol": symbol, "valid": False, "current_price": None}
    except RequestException as e:
        raise ConnectionError("Network error while contacting price service") from e
