#!/bin/bash

echo "Creating Kafka topic: ride_events"

docker exec -it kafka kafka-topics --create \
--topic ride_events \
--bootstrap-server localhost:9092 \
--partitions 1 \
--replication-factor 1

echo "Topic created successfully!"