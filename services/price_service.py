import yfinance as yf
from requests.exceptions import RequestException
from typing import Dict, Union
from datetime import datetime
import re


class InvalidSymbolError(Exception):
    """Raised when the provided ticker symbol is invalid or not found."""
    pass


class InvalidDateError(Exception):
    """Raised when the provided date is invalid or in wrong format."""
    pass


class NetworkError(Exception):
    """Raised when there is a network error while fetching price data."""
    pass


def _validate_ticker_symbol(symbol: str) -> yf.Ticker:
    """
    Validate ticker symbol and return ticker object.
    
    Args:
        symbol (str): The ticker symbol to validate
        
    Returns:
        yf.Ticker: Valid ticker object
        
    Raises:
        InvalidSymbolError: If the symbol is invalid or not found
    """
    ticker = yf.Ticker(symbol)
    info = ticker.info
    
    # Check if symbol exists and matches
    if "symbol" not in info or info["symbol"] != symbol:
        raise InvalidSymbolError(f"Invalid ticker symbol: {symbol}")
    
    return ticker


def _validate_date_format(date_str: str) -> str:
    """
    Validate date format YYYY-MM-DD.
    
    Args:
        date_str (str): Date string to validate
        
    Returns:
        str: Validated date string
        
    Raises:
        InvalidDateError: If date format is invalid
    """
    # Check format with regex
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        raise InvalidDateError(f"Invalid date format. Expected YYYY-MM-DD, got: {date_str}")
    
    # Validate date is actually valid
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError as e:
        raise InvalidDateError(f"Invalid date: {date_str}. {str(e)}")
    
    return date_str


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
        # Validate ticker symbol
        ticker = _validate_ticker_symbol(symbol)
        
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


def get_historical_price(symbol: str, date: str) -> Dict[str, Union[str, float]]:
    """
    Get the historical price of a given ticker symbol for a specific date.
    If no price data is available for the exact date, returns the price from
    the closest prior trading date.
    
    Args:
        symbol (str): The ticker symbol to get the price for (e.g., 'AAPL', 'MSFT')
        date (str): Date in YYYY-MM-DD format (e.g., '2024-01-15')
        
    Returns:
        Dict[str, Union[str, float]]: Dictionary containing symbol, date, and historical price
        
    Raises:
        InvalidSymbolError: If the symbol is invalid or not found
        InvalidDateError: If the date format is invalid
        NetworkError: If there is a network error while fetching data
    """
    try:
        # Validate date format
        validated_date = _validate_date_format(date)
        
        # Validate ticker symbol
        ticker = _validate_ticker_symbol(symbol)
        
        # Get historical data for the specific date (end is not inclusive, so add 1 day)
        from datetime import datetime, timedelta
        request_date = datetime.strptime(validated_date, '%Y-%m-%d')
        end_date = request_date + timedelta(days=1)
        
        history = ticker.history(start=validated_date, end=end_date.strftime('%Y-%m-%d'))
        
        # If no data for exact date, try to get data from a wider range to find closest prior date
        if len(history) == 0:
            # Get data from 30 days before the requested date to find the closest prior trading date
            from datetime import datetime, timedelta
            request_date = datetime.strptime(validated_date, '%Y-%m-%d')
            start_date = request_date - timedelta(days=30)
            
            # Get historical data for the wider range (end is not inclusive, so add 1 day)
            history = ticker.history(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
            
            if len(history) == 0:
                raise InvalidSymbolError(f"No price data available for symbol {symbol} on or before date {validated_date}")
            
            # Get the closest prior trading date
            closest_date = history.index[-1].strftime('%Y-%m-%d')
            historical_price = history["Close"].iloc[-1]
            
            # Validate that we have a valid numeric price
            if historical_price is None or (hasattr(historical_price, 'isna') and historical_price.isna()):
                raise InvalidSymbolError(f"No valid price data for symbol {symbol} on or before date {validated_date}")
            
            return {
                "symbol": symbol,
                "date": validated_date,
                "actual_date": closest_date,
                "historical_price": float(historical_price)
            }
        else:
            # We have data for the exact date
            historical_price = history["Close"].iloc[0]
            
            # Validate that we have a valid numeric price
            if historical_price is None or (hasattr(historical_price, 'isna') and historical_price.isna()):
                raise InvalidSymbolError(f"No valid price data for symbol {symbol} on date {validated_date}")
            
            return {
                "symbol": symbol,
                "date": validated_date,
                "historical_price": float(historical_price)
            }
        
    except RequestException as e:
        raise ConnectionError("Network error while contacting price service") from e
    except (InvalidSymbolError, InvalidDateError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Catch any other unexpected errors and treat as invalid symbol
        raise InvalidSymbolError(f"Error fetching historical price for symbol {symbol} on date {date}: {str(e)}") from e
