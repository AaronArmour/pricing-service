# Pricing Service API

A simple FastAPI service that validates stock ticker symbols and retrieves prices using yfinance.

## Table of Contents

- [Quick Usage](#quick-usage)
- [Overview](#overview)
- [Features](#features)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Running Tests](#running-tests)

## Quick Usage

```bash
# Get current price for Google stock
curl "http://localhost:8000/api/price?symbol=GOOGL"

# Get historical price for a specific date
curl "http://localhost:8000/api/price?symbol=GOOGL&date=2024-01-15"
```

## Overview

This API provides a backend service to validate stock tickers and retrieve real-time prices. Designed as part of a personal portfolio tracker MVP.

## Features

- Validate ticker symbols
- Fetch current market prices
- Fetch historical market prices

## Getting Started

### Prerequisites

- Python 3.12+
- pip

### Installation

```bash
git clone https://github.com/aaronarmour/pricing-service.git
cd pricing-service
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### Running the API
```
uvicorn app.main:app --reload
```

## API Endpoints

### GET /api/check_symbol

**Description:**  
Validates whether a given stock ticker symbol exists and is currently trading.

**Query Parameters:**

| Name   | Type   | Required | Description                               |
|--------|--------|----------|-------------------------------------------|
| symbol | string |  Y       | The stock ticker symbol (e.g., `GOOGL`)    |

#### Example Request

GET /api/check_symbol?symbol=GOOGL

####  Example Response
```json
{
  "symbol": "GOOGL",
  "valid": true,
  "current_price": 195.0399932861328
}
```

### GET /api/price

**Query Parameters:**

| Name   | Type   | Required | Description                            |
| ------ | ------ | -------- | -------------------------------------- |
| symbol | string |  Y       | The stock ticker symbol                |
| date   | string |  N       | Date in `YYYY-MM-DD` format (optional) |

#### Example Request

GET /api/price?symbol=GOOGL

####  Example Response
```json
{
  "symbol": "GOOGL",
  "valid": true,
  "current_price": 195.0399932861328
}
```

#### Example Request

GET /api/price?symbol=GOOGL&date=2024-01-15

####  Example Response
```json
{
  "symbol": "GOOGL",
  "date":"2024-01-15",
  "actual_date":"2024-01-12",
  "historical_price":142.64999389648438
}
```

## Running Tests

Run the test suite using pytest:

```bash
python -m pytest -v
```
