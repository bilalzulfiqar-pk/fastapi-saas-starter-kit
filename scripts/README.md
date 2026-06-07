# Scripts

This folder contains optional helper scripts that make runtime verification or maintenance easier without becoming required parts of the default developer workflow.

## Available helpers

### `python scripts/verify_redis_rate_limit.py`

Optional runtime check for the Redis-backed rate limiter path in the local Docker stack.

What it verifies:

- the API is reachable
- repeated failed logins eventually return `429`
- recent API logs do not show the `Falling back to in-memory rate limiter` warning

When to use it:

- before publishing a public starter update
- after changing rate-limiter code
- when you want stronger confidence that Redis is actually being used in the live local stack
