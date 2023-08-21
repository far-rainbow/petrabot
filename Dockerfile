# syntax=docker/dockerfile:1
FROM kamenka/petrobot:python
WORKDIR /app
COPY . .
CMD ["python3","petrabot.py"]
