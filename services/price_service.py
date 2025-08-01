import yfinance as yf
from requests.exceptions import RequestException
from typing import Dict, Union


class InvalidSymbolError(Exception):
    """Raised when the provided ticker symbol is invalid or not found."""
    pass


class NetworkError(Exception):
    """Raised when there is a network error while fetching price data."""
    pass


def get_current_price(symbol: str) -> Dict[str, Union[str, float]]:
    """
    Get the current price of a given ticker symbol using yfinance.
    
    Args:
        symbol (str): The ticker symbol to get the price for (e.g., 'AAPL', 'MSFT')
        
    Returns:
        Dict[str, Union[str, float]]: Dictionary containing symbol and current price
        
    Raises:
        InvalidSymbolError: If the symbol is invalid or not found
        NetworkError: If there is a network error while fetching data
    """
    try:
        # Create ticker object
        ticker = yf.Ticker(symbol)
        
        # Get ticker info to validate symbol
        info = ticker.info
        
        # Check if symbol exists and matches
        if "symbol" not in info or info["symbol"] != symbol:
            raise InvalidSymbolError(f"Invalid ticker symbol: {symbol}")
        
        # Get current price using history method
        history = ticker.history(period="1d")
        
        # Check if we have valid price data
        if len(history) == 0:
            raise InvalidSymbolError(f"No price data available for symbol: {symbol}")
        
        current_price = history["Close"].iloc[0]
        
        # Validate that we have a valid numeric price
        if current_price is None or (hasattr(current_price, 'isna') and current_price.isna()):
            raise InvalidSymbolError(f"No valid price data for symbol: {symbol}")
        
        return {
            "symbol": symbol,
            "current_price": float(current_price)
        }
        
    except RequestException as e:
        raise ConnectionError("Network error while contacting price service") from e
    except InvalidSymbolError:
        # Re-raise our custom exception
        raise
    except Exception as e:
        # Catch any other unexpected errors and treat as invalid symbol
        raise InvalidSymbolError(f"Error fetching price for symbol {symbol}: {str(e)}") from e
