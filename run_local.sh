#!/bin/bash

export DOCKER_BUILDKIT=1
export ENVIRONMENT=${1:-development}

echo "Running environment: $ENVIRONMENT"

docker compose down --remove-orphans

docker compose -f docker-compose.yml up --build