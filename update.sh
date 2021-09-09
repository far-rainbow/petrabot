#!/bin/sh
git pull
make
docker stack deploy -c docker-compose.yml petrabot
