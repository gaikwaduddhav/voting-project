# Multi-Service Voting App 🗳️

A production-ready voting application built with Docker, featuring 5 interconnected services with healthchecks, auto-restart policies, and multi-stage builds.

## Architecture


## Services

| Service | Port | Purpose |
|---------|------|---------|
| Frontend | 3000 | Web interface |
| API | 8080 | REST API for voting |
| Redis | 6379 | Cache & message queue |
| Worker | - | Processes votes |
| PostgreSQL | 5432 | Persistent storage |

## Quick Start

```bash
# Clone and setup
git clone <your-repo>
cd voting-app

# Make scripts executable
chmod +x scripts/*.sh

# Run setup (generates secrets, builds, starts)
./scripts/setup.sh

# Access the app
open http://localhost:3000

## Services

| Service | Port | Purpose |
|---------|------|---------|
| Frontend | 3000 | Web interface |
| API | 8080 | REST API for voting |
| Redis | 6379 | Cache & message queue |
| Worker | - | Processes votes |
| PostgreSQL | 5432 | Persistent storage |

## Quick Start

```bash
# Clone and setup
git clone <your-repo>
cd voting-app

# Make scripts executable
chmod +x scripts/*.sh

# Run setup (generates secrets, builds, starts)
./scripts/setup.sh

# Access the app
open http://localhost:3000


Docker Features Demonstrated
✅ Multi-stage builds - Reduces image size by 85%

✅ Healthchecks - Automatic container health monitoring

✅ Custom networks - Network isolation (database-net is internal)

✅ Volume persistence - Redis and PostgreSQL data persists

✅ Resource limits - CPU and memory constraints per service

✅ Restart policies - Auto-restart on failure

✅ Secrets management - Database passwords via Docker secrets

✅ Dependency management - depends_on with condition




# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Scale worker
docker-compose up -d --scale worker=3

# Check health
./scripts/healthcheck.sh

# Run load test
./scripts/load-test.sh

# Stop everything
docker-compose down

# Stop and remove volumes
docker-compose down -v



# Check container logs
docker logs voting-api
docker logs voting-worker

# Check health status
docker inspect --format='{{.State.Health.Status}}' voting-api

# Enter container
docker exec -it voting-api /bin/bash






Learning Resources
Docker Multi-stage Builds

Docker Healthchecks

Docker Compose Networking
