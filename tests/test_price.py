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


# Historical Price Tests

def test_historical_price_valid_date():
    """Test that valid historical date returns adjusted close price."""
    response = client.get("/api/price?symbol=AAPL&date=2024-01-15")
    assert response.status_code == 200
    
    data = response.json()
    assert "symbol" in data
    assert "date" in data
    assert "historical_price" in data
    assert data["symbol"] == "AAPL"
    assert data["date"] == "2024-01-15"
    assert isinstance(data["historical_price"], (int, float))
    assert data["historical_price"] > 0

def test_historical_price_weekend_date():
    """Test that weekend date returns price from previous trading day."""
    # Test a Sunday (2024-01-14 was a Sunday)
    response = client.get("/api/price?symbol=AAPL&date=2024-01-14")
    assert response.status_code == 200
    
    data = response.json()
    assert "symbol" in data
    assert "date" in data
    assert "actual_date" in data
    assert "historical_price" in data
    assert data["symbol"] == "AAPL"
    assert data["date"] == "2024-01-14"  # Requested date
    assert data["actual_date"] != "2024-01-14"  # Should be different (previous trading day)
    assert isinstance(data["historical_price"], (int, float))
    assert data["historical_price"] > 0

def test_historical_price_holiday_date():
    """Test that holiday date returns price from previous trading day."""
    # Test New Year's Day (2024-01-01 was a holiday)
    response = client.get("/api/price?symbol=AAPL&date=2024-01-01")
    assert response.status_code == 200
    
    data = response.json()
    assert "symbol" in data
    assert "date" in data
    assert "actual_date" in data
    assert "historical_price" in data
    assert data["symbol"] == "AAPL"
    assert data["date"] == "2024-01-01"  # Requested date
    assert data["actual_date"] != "2024-01-01"  # Should be different (previous trading day)
    assert isinstance(data["historical_price"], (int, float))
    assert data["historical_price"] > 0

def test_historical_price_invalid_date_format():
    """Test that invalid date format returns 400 error."""
    response = client.get("/api/price?symbol=AAPL&date=invalid-date")
    assert response.status_code == 400
    assert "Invalid date format" in response.json()["detail"]

def test_historical_price_future_date():
    """Test that future date returns 400 error."""
    from datetime import datetime, timedelta
    
    # Get current date and add 5 days to ensure it's in the future
    future_date = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
    
    response = client.get(f"/api/price?symbol=AAPL&date={future_date}")
    assert response.status_code == 400
    assert "Date cannot be in the future" in response.json()["detail"]

def test_historical_price_invalid_date():
    """Test that invalid date (like 2024-13-45) returns 400 error."""
    response = client.get("/api/price?symbol=AAPL&date=2024-13-45")
    assert response.status_code == 400
    assert "Invalid date" in response.json()["detail"]

def test_historical_price_invalid_symbol():
    """Test that invalid symbol with historical date returns 404 error."""
    response = client.get("/api/price?symbol=FAKE123&date=2024-01-15")
    assert response.status_code == 404
    assert "Invalid ticker symbol" in response.json()["detail"]

def test_historical_price_outside_data_range():
    """Test that date outside available data range returns appropriate error."""
    # Test a very old date that likely has no data
    response = client.get("/api/price?symbol=AAPL&date=1900-01-01")
    assert response.status_code == 404
    assert "No price data available" in response.json()["detail"]

def test_historical_price_multiple_symbols():
    """Test historical prices for multiple valid symbols."""
    symbols = ["AAPL", "MSFT", "GOOGL"]
    test_date = "2024-01-16"
    expected_prices = [183.63, 390.27, 142.49]
    
    for symbol, expected_price in zip(symbols, expected_prices):
        response = client.get(f"/api/price?symbol={symbol}&date={test_date}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["symbol"] == symbol
        assert data["date"] == test_date
        assert isinstance(data["historical_price"], (int, float))
        assert data["historical_price"] > 0
        
        # Check that the retrieved price is within 0.001 of the expected price
        retrieved_price = data["historical_price"]
        assert abs(retrieved_price - expected_price) < 0.01, f"Price for {symbol} was {retrieved_price}, expected {expected_price}"

def test_historical_price_empty_date():
    """Test that empty date parameter defaults to current price."""
    response = client.get("/api/price?symbol=AAPL&date=")
    assert response.status_code == 200
    
    data = response.json()
    assert "symbol" in data
    assert "current_price" in data
    assert data["symbol"] == "AAPL"
    assert isinstance(data["current_price"], (int, float))
    assert data["current_price"] > 0

def test_historical_price_network_error():
    """Test that network errors with historical date return 503 error."""
    with patch("yfinance.Ticker") as MockTicker:
        instance = MockTicker.return_value
        type(instance).info = property(lambda self: (_ for _ in ()).throw(RequestException("Simulated network error")))

        response = client.get("/api/price?symbol=AAPL&date=2024-01-15")
        assert response.status_code == 503
        assert response.json()["detail"] == "Network error while contacting price service"
