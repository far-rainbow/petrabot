# syntax=docker/dockerfile:1
FROM kamenka/petrabot:python
WORKDIR /app
COPY . .
CMD ["python3","petrabot.py"]
