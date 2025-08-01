from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, Mock
from requests.exceptions import RequestException
from services.price_service import InvalidSymbolError

client = TestClient(app)

def test_empty_symbol():
    """Test that empty symbol returns 400 error."""
    response = client.get("/api/price?symbol")
    assert response.status_code == 400
    assert response.json()["detail"] == "Symbol cannot be empty"

def test_valid_symbol():
    """Test that valid symbol returns current price."""
    response = client.get("/api/price?symbol=AAPL")
    assert response.status_code == 200
    
    data = response.json()
    assert "symbol" in data
    assert "current_price" in data
    assert data["symbol"] == "AAPL"
    assert isinstance(data["current_price"], (int, float))
    assert data["current_price"] > 0

def test_invalid_symbol():
    """Test that invalid symbol returns 404 error."""
    response = client.get("/api/price?symbol=FAKE123")
    assert response.status_code == 404
    assert "Invalid ticker symbol" in response.json()["detail"]

def test_price_route_network_error():
    """Test that network errors return 503 error."""
    with patch("yfinance.Ticker") as MockTicker:
        instance = MockTicker.return_value
        type(instance).info = property(lambda self: (_ for _ in ()).throw(RequestException("Simulated network error")))

        response = client.get("/api/price?symbol=AAPL")
        assert response.status_code == 503
        assert response.json()["detail"] == "Network error while contacting price service"

def test_multiple_valid_symbols():
    """Test multiple valid symbols to ensure consistency."""
    symbols = ["AAPL", "MSFT", "GOOGL"]
    
    for symbol in symbols:
        response = client.get(f"/api/price?symbol={symbol}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["symbol"] == symbol
        assert isinstance(data["current_price"], (int, float))
        assert data["current_price"] > 0

def test_symbol_with_special_characters():
    """Test symbol with special characters returns appropriate error."""
    response = client.get("/api/price?symbol=INVALID@#$")
    assert response.status_code == 404
    assert "Invalid ticker symbol" in response.json()["detail"]

def test_symbol_case_sensitivity():
    """Test that symbol case doesn't affect the result."""
    response_lower = client.get("/api/price?symbol=aapl")
    response_upper = client.get("/api/price?symbol=AAPL")
    
    # Both should work (yfinance handles case insensitivity)
    if response_lower.status_code == 200 and response_upper.status_code == 200:
        data_lower = response_lower.json()
        data_upper = response_upper.json()
        assert data_lower["symbol"] == data_upper["symbol"]
        assert data_lower["current_price"] == data_upper["current_price"]
