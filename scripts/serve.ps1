param([int]$Port = 8021)
$env:DATABASE_URL = "sqlite:///./data/MarketLens.db"
uvicorn app.api.main:app --host 127.0.0.1 --port $Port --reload
