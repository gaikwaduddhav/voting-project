#!/usr/bin/env python3
import time
import os

print("Simple Worker Started")
print(f"Redis Host: {os.getenv('REDIS_HOST', 'not set')}")
print(f"Postgres Host: {os.getenv('POSTGRES_HOST', 'not set')}")

while True:
    print("Worker is alive and running...")
    time.sleep(10)
