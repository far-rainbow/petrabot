all: python update

python:
	docker build --no-cache --tag kamenka/petrabot:python -f Dockerfile.python .
	docker image push kamenka/petrabot:python
update:
	git config pull.ff only
	git pull
	docker build --tag kamenka/petrabot:latest .
	PETRABOT_IMAGE_ID=$$(docker images -q kamenka/petrabot:latest) docker stack deploy -c docker-compose.yml petrabot
	docker image push kamenka/petrabot:latest
