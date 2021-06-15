all:
	docker build --tag petrabot-docker .
	docker run petrabot-docker
