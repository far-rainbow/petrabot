# syntax=docker/dockerfile:1
FROM python:3.9-slim-buster

WORKDIR /app
COPY . .
RUN apt update && apt upgrade -y && \
    apt install fortune -y && \
    apt install fortunes-ru -y && \
    apt install fortunes-bofh-excuses -y && \
    pip3 install -r requirements.txt && \
    python pip_upgrade_all.py

CMD ["python3","petrabot.py"]
