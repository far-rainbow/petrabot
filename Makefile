all:
	docker build --tag kamenka/petrabot:govorun .
	docker image push kamenka/petrabot:govorun

