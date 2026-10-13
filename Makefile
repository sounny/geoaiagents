.PHONY: help install test

help:
	@echo "Available commands:"
	@echo "  make install  - Install dependencies from requirements.txt"
	@echo "  make test     - Run tests using pytest"
	@echo "  make help     - Show this help message"

install:
	pip install -r requirements.txt

test:
	pytest
