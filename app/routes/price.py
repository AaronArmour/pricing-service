from fastapi import APIRouter, HTTPException
from services.price_service import get_current_price, InvalidSymbolError

router = APIRouter()

@router.get("/price")
def read_price(symbol: str = ""):
    if not symbol or len(symbol) == 0:
        raise HTTPException(status_code=400, detail="Symbol cannot be empty")
    
    try:
        return get_current_price(symbol)
    except InvalidSymbolError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error") 