PYTHON ?= python
VENV_DIR := backend.venv
BACKEND_DIR := backend
ENV_FILE := $(BACKEND_DIR)/.env
PYTHON_VENV := $(shell if [ -x "$(VENV_DIR)/Scripts/python.exe" ]; then echo "$(VENV_DIR)/Scripts/python.exe"; elif [ -x "$(VENV_DIR)/bin/python" ]; then echo "$(VENV_DIR)/bin/python"; else echo "$(PYTHON)"; fi)

.PHONY: help install env db seed run test health clean

help:
	@echo "Available commands:"
	@echo "  make install     - create venv and install backend dependencies"
	@echo "  make env         - create .env from .env.example if missing"
	@echo "  make db          - initialize the SQLite database tables"
	@echo "  make seed        - load sample demo data"
	@echo "  make run         - start the Flask API server"
	@echo "  make test        - run backend tests"
	@echo "  make health      - check /api/health"
	@echo "  make clean       - remove the venv and local generated files"

install:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Installing backend dependencies..."
	$(PYTHON_VENV) -m pip install --upgrade pip
	$(PYTHON_VENV) -m pip install -r "$(BACKEND_DIR)/requirements.txt"

env:
	@if [ ! -f "$(ENV_FILE)" ]; then \
		cp "$(BACKEND_DIR)/.env.example" "$(ENV_FILE)"; \
		echo "Created $(ENV_FILE) from .env.example"; \
	else \
		echo "$(ENV_FILE) already exists."; \
	fi
	@echo "For local development, keep: USE_SQLITE=True"

db:
	@echo "Initializing database..."
	$(PYTHON_VENV) "$(BACKEND_DIR)/database/init_db.py"

seed:
	@echo "Loading sample data..."
	$(PYTHON_VENV) "$(BACKEND_DIR)/database/seed_data.py"

run:
	@echo "Starting Flask backend on http://localhost:5000"
	$(PYTHON_VENV) "$(BACKEND_DIR)/run.py"

test:
	@echo "Running backend tests..."
	$(PYTHON_VENV) -m pytest "$(BACKEND_DIR)" -q

health:
	@curl -s http://localhost:5000/api/health || echo "Server is not running yet. Run 'make run' first."

clean:
	@echo "Removing local virtual environment and generated files..."
	@rm -rf "$(VENV_DIR)"
	@rm -f "$(BACKEND_DIR)/pothole_ai.db"
	@rm -f "$(ENV_FILE)"
	@echo "Cleaned local backend environment."
