all: python update

python:
	docker build --no-cache --tag kamenka/petrabot:python -f Dockerfile.python .
	docker image push kamenka/petrabot:python
update:
	git pull
	docker build --tag kamenka/petrabot:latest .
	docker stack deploy -c docker-compose.yml petrabot
	docker image push kamenka/petrabot:latest
