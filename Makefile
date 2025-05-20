VERSION := 0.1.0

setup:
	poetry install

run:
	@poetry run hypercorn src.main:app --reload

run-migrations:
	@mongodb-migrate --url 'mongodb://127.0.0.1:27017/judge?replicaSet=rs0' --migrations migrations --database judge

lint:
	blue .
