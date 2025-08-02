from fastapi import APIRouter, HTTPException
from services.price_service import get_current_price, get_historical_price, InvalidSymbolError, InvalidDateError
import re
from datetime import datetime

router = APIRouter()

def validate_date_format(date_str: str) -> str:
    """
    Validate date format YYYY-MM-DD.
    
    Args:
        date_str (str): Date string to validate
        
    Returns:
        str: Validated date string
        
    Raises:
        HTTPException: If date format is invalid
    """
    # Check format with regex
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        raise HTTPException(status_code=400, detail=f"Invalid date format. Expected YYYY-MM-DD, got: {date_str}")
    
    # Validate date is actually valid
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date: {date_str}. {str(e)}")
    
    return date_str

@router.get("/price")
def read_price(symbol: str = "", date: str = None):
    if not symbol or len(symbol) == 0:
        raise HTTPException(status_code=400, detail="Symbol cannot be empty")
    
    try:
        if date:
            # Validate date format
            validated_date = validate_date_format(date)
            return get_historical_price(symbol, validated_date)
        else:
            return get_current_price(symbol)
    except InvalidSymbolError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidDateError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error")
