from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch
from requests.exceptions import RequestException

client = TestClient(app)

def test_empty_symbol():
    response = client.get("/api/check_symbol?symbol")
    assert response.status_code == 400

def test_valid_symbol():
    response = client.get("/api/check_symbol?symbol=AAPL")
    assert response.status_code == 200
    assert response.json()["valid"] is True, "Expected 'valid' to be True"

def test_invalid_symbol():
    response = client.get("/api/check_symbol?symbol=FAKE123")
    assert response.status_code == 200
    assert response.json()["valid"] is False, "Expected 'valid' to be False"

def test_check_symbol_route_network_error():
    with patch("yfinance.Ticker") as MockTicker:
        instance = MockTicker.return_value
        type(instance).info = property(lambda self: (_ for _ in ()).throw(RequestException("Simulated network error")))

        response = client.get("/api/check_symbol?symbol=AAPL")
        assert response.status_code == 503
        assert response.json()["detail"] == "Network error while contacting price service"
