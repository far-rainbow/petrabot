all:
	docker build --tag kamenka/petrabot:latest .
	docker image push kamenka/petrabot:latest

