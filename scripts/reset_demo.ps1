$env:DATABASE_URL = "sqlite:///./data/MarketLens.db"
python -m app.jobs.run_pipeline --domain co2_us_market --mode reset-demo
