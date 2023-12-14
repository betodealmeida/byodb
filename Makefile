test:
	poetry run pytest --cov=src/byodb --cov-report term-missing tests/

check:
	pre-commit run -a
