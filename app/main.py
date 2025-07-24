from fastapi import FastAPI, HTTPException
from services.ticker_check_service import check_symbol

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "query": q}

@app.get("/check_symbol")
def read_symbol_check(symbol: str = ""):
    if not symbol or len(symbol) == 0:
        raise HTTPException(status_code=400, detail="Symbol cannot be empty")
    
    try:
        return check_symbol(symbol)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))