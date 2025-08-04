import re
from datetime import datetime
import yfinance as yf


class InvalidDateError(Exception):
    """Raised when the provided date is invalid or in wrong format."""
    pass


class InvalidSymbolError(Exception):
    """Raised when the provided ticker symbol is invalid or not found."""
    pass


def validate_date_format(date_str: str) -> str:
    """
    Validate date format YYYY-MM-DD and ensure it's not in the future.
    
    Args:
        date_str (str): Date string to validate
        
    Returns:
        str: Validated date string
        
    Raises:
        InvalidDateError: If date format is invalid or date is in the future
    """
    # Check format with regex
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        raise InvalidDateError(f"Invalid date format. Expected YYYY-MM-DD, got: {date_str}")
    
    # Validate date is actually valid
    try:
        request_date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError as e:
        raise InvalidDateError(f"Invalid date: {date_str}. {str(e)}")
    
    # Check if date is in the future
    today = datetime.now().date()
    if request_date.date() > today:
        raise InvalidDateError(f"Date cannot be in the future. Requested: {date_str}, Today: {today.strftime('%Y-%m-%d')}")
    
    return date_str


def validate_ticker_symbol(symbol: str) -> yf.Ticker:
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
