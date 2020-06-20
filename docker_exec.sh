#!/usr/bin/env bash
docker exec -it  hakaton_20_mongo-container_1 mongo --authenticationDatabase "admin" -u "root" -p "root"
