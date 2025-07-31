from fastapi import APIRouter, HTTPException
from services.ticker_check_service import check_symbol

router = APIRouter()

@router.get("/check_symbol")
def read_symbol_check(symbol: str = ""):
    if not symbol or len(symbol) == 0:
        raise HTTPException(status_code=400, detail="Symbol cannot be empty")
    
    try:
        return check_symbol(symbol)
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error")