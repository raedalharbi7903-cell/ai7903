.PHONY: install run test lint format check-format migrate

install:
	python -m pip install -r backend/requirements/dev.txt
run:
	python -m uvicorn app.main:app --app-dir backend --reload
test:
	python -m pytest backend/tests
lint:
	python -m ruff check backend
format:
	python -m black backend
check-format:
	python -m black --check backend
migrate:
	cd backend && python -m alembic upgrade head

