run-api:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

run-web:
	python -m http.server 5173

smoke:
	python scripts/sse_smoke.py
