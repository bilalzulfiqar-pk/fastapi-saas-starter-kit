# Scripts

This folder is reserved for helper scripts such as seeding, reset, and deployment utilities.
The MVP keeps the logic inside app services and Docker commands first, then adds scripts only when they remove real friction.

## Available helpers

- `python scripts/verify_redis_rate_limit.py`
  Optional runtime check for the Redis-backed rate limiter path in the local Docker stack.
