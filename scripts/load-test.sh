#!/bin/bash

# Simple load test
echo "=== Running Load Test ==="
echo "Sending 100 votes..."

for i in {1..100}; do
    CANDIDATE="candidate_$((RANDOM % 3 + 1 | sed 's/1/a/;s/2/b/;s/3/c/'))"
    curl -s -X POST http://localhost:8080/vote \
        -H "Content-Type: application/json" \
        -d "{\"candidate\":\"$CANDIDATE\"}" > /dev/null
    
    if [ $((i % 10)) -eq 0 ]; then
        echo "Sent $i votes..."
    fi
done

echo "✓ Load test complete"
echo "Check results at http://localhost:3000"
