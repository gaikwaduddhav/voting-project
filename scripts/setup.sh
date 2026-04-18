#!/bin/bash

# Setup script for voting app
set -e

echo "=== Voting App Setup ==="

# Create secrets directory if not exists
mkdir -p secrets

# Generate random database password
DB_PASSWORD=$(openssl rand -base64 32)
echo "$DB_PASSWORD" > secrets/db_password.txt
chmod 600 secrets/db_password.txt

# Create db.env file
cat > secrets/db.env << EOF
POSTGRES_PASSWORD=$DB_PASSWORD
EOF

# Generate Redis password
REDIS_PASSWORD=$(openssl rand -base64 32)
echo "REDIS_PASSWORD=$REDIS_PASSWORD" > .env

echo "✓ Secrets generated"

# Build and start containers
echo "Building Docker images..."
docker-compose build --parallel

echo "Starting services..."
docker-compose up -d

echo "Waiting for services to be healthy..."
sleep 10

# Check service health
echo "Checking service health..."
docker-compose ps

echo "=== Setup Complete ==="
echo "Frontend: http://localhost:3000"
echo "API: http://localhost:8080"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo "To stop and remove volumes: docker-compose down -v"
