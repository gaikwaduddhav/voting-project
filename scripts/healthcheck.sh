#!/bin/bash

# Health check script
echo "=== Voting App Health Check ==="

# Check frontend
if curl -s http://localhost:3000/health > /dev/null; then
    echo "✓ Frontend: Healthy"
else
    echo "✗ Frontend: Unhealthy"
fi

# Check API
if curl -s http://localhost:8080/health > /dev/null; then
    echo "✓ API: Healthy"
else
    echo "✗ API: Unhealthy"
fi

# Check Redis
if docker exec voting-redis redis-cli PING > /dev/null 2>&1; then
    echo "✓ Redis: Healthy"
else
    echo "✗ Redis: Unhealthy"
fi

# Check PostgreSQL
if docker exec voting-postgres pg_isready -U voting_app > /dev/null 2>&1; then
    echo "✓ PostgreSQL: Healthy"
else
    echo "✗ PostgreSQL: Unhealthy"
fi

# Check Worker
WORKER_RUNNING=$(docker ps --filter "name=voting-worker" --format "{{.Status}}" | grep -c "Up")
if [ "$WORKER_RUNNING" -eq 1 ]; then
    echo "✓ Worker: Running"
else
    echo "✗ Worker: Not running"
fi

echo ""
echo "=== Container Statistics ==="
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
