all: python update

python:
	docker build --no-cache --tag kamenka/petrobot:python -f Dockerfile.python .
	#docker image push kamenka/petrobot:python
update:
	git config pull.ff only
	git pull
	docker build --tag kamenka/petrobot:latest .
	PETRABOT_IMAGE_ID=$$(docker images -q kamenka/petrobot:latest) docker compose -f docker-compose.yml up -d
	#docker image push kamenka/petrobot:latest
