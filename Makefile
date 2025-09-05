.PHONY: run
PY := .venv/Scripts/python.exe

run:
	$(PY) -m uvicorn app.main:app --host 127.0.0.1 --port 3001 --reload
