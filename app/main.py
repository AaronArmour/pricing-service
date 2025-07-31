from fastapi import FastAPI
from app.routes import check_symbol

app = FastAPI()
app.include_router(check_symbol.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "query": q}
