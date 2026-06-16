.PHONY: reset-demo test serve install

install:
	python -m pip install -e .[dev]

reset-demo:
	python -m app.jobs.run_pipeline --domain co2_us_market --mode reset-demo

test:
	pytest tests/ -q

serve:
	uvicorn app.api.main:app --host 127.0.0.1 --port 8021 --reload
