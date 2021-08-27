all:
	docker build --tag kamenka/petrabot .
	docker image push kamenka/petrabot:latest

