from fastapi import APIRouter, HTTPException
from services.price_service import get_current_price, get_historical_price
from utils.validation import validate_date_format, InvalidSymbolError, InvalidDateError

router = APIRouter()

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
