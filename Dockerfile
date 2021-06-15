# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster

RUN apt update && apt upgrade -y && \
    apt install fortune -y && \
    apt install fortunes-ru -y && \
    apt install fortunes-bofh-excuses -y
   
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD ["python3","petrabot.py"]
