.PHONY: install run test format lint clean

install:
	pip install -r requirements.txt

run:
	python main.py

test:
	pytest tests/

format:
	black .
	isort .

lint:
	flake8 .
	mypy .

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
