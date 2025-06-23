#!/bin/bash

# Stop all services safely (do NOT delete volumes)
docker-compose down --remove-orphans

# Pull latest changes
git pull origin

# Rebuild everything cleanly
docker-compose build --no-cache

# Start services with forced recreation
docker-compose up -d --force-recreate
