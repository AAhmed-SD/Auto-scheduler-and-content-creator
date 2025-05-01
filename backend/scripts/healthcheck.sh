#!/bin/bash

# Check if the application is responding
curl -f http://localhost:8000/health || exit 1

# Check if we can connect to the database
nc -z db 5432 || exit 1

# Check if we can connect to Redis
nc -z redis 6379 || exit 1

exit 0 