from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib import error, request

REPO_ROOT = Path(__file__).resolve().parents[1]
FALLBACK_WARNING = "Falling back to in-memory rate limiter"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Optionally verify that the Redis-backed rate limiter path is active in the local Docker stack."
    )
    parser.add_argument("--api-url", default="http://localhost:8000", help="Base API URL")
    parser.add_argument("--origin", default="http://localhost:3000", help="Trusted frontend origin header")
    parser.add_argument("--email", default="redis-check@example.com", help="Email used for repeated failed login attempts")
    parser.add_argument(
        "--password",
        default="wrongpass123",
        help="Wrong password used to trigger login rate limiting",
    )
    parser.add_argument(
        "--attempts",
        type=int,
        default=6,
        help="Number of failed login attempts to send; should be higher than the configured login limit",
    )
    parser.add_argument(
        "--service",
        default="api",
        help="Docker Compose service name to inspect for fallback warnings",
    )
    parser.add_argument(
        "--skip-log-check",
        action="store_true",
        help="Only verify the 429 behavior and skip Docker log inspection",
    )
    return parser


def request_json(method: str, url: str, *, headers: dict[str, str] | None = None, payload: dict[str, Any] | None = None) -> tuple[int, dict[str, Any] | None]:
    body = None
    request_headers = {"Accept": "application/json"}
    if headers:
        request_headers.update(headers)
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        request_headers["Content-Type"] = "application/json"

    req = request.Request(url, method=method, headers=request_headers, data=body)
    try:
        with request.urlopen(req, timeout=15) as response:
            data = response.read().decode("utf-8")
            return response.status, json.loads(data) if data else None
    except error.HTTPError as exc:
        data = exc.read().decode("utf-8")
        return exc.code, json.loads(data) if data else None


def ensure_api_is_ready(api_url: str) -> None:
    status, _ = request_json("GET", f"{api_url.rstrip('/')}/health")
    if status != 200:
        raise RuntimeError(f"API health check failed with status {status}. Start the stack before running this verifier.")


def inspect_logs_since(service: str, since_utc: str) -> str:
    command = ["docker", "compose", "logs", "--since", since_utc, service]
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Unable to inspect Docker Compose logs.")
    return result.stdout


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    api_url = args.api_url.rstrip("/")
    started_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        ensure_api_is_ready(api_url)
    except Exception as exc:  # noqa: BLE001
        print(f"[error] {exc}")
        return 1

    print(f"[info] Checking login rate limiting at {api_url}/api/v1/auth/login")
    print(f"[info] Using Origin: {args.origin}")
    print("[info] Repeated failed login attempts are expected in this check.")

    saw_rate_limit = False
    for attempt in range(1, args.attempts + 1):
        status, payload = request_json(
            "POST",
            f"{api_url}/api/v1/auth/login",
            headers={"Origin": args.origin},
            payload={"email": args.email, "password": args.password},
        )
        error_code = payload.get("error", {}).get("code") if isinstance(payload, dict) else None
        print(f"[attempt {attempt}/{args.attempts}] status={status} code={error_code}")
        if status == 429:
            saw_rate_limit = True
            break

    if not saw_rate_limit:
        print("[error] The login endpoint never returned 429. The rate limiter may not be active.")
        return 1

    if args.skip_log_check:
        print("[ok] Received 429 from the login endpoint. Log inspection was skipped.")
        return 0

    try:
        logs = inspect_logs_since(args.service, started_at)
    except Exception as exc:  # noqa: BLE001
        print(f"[error] Received 429, but could not inspect Docker logs: {exc}")
        print("[hint] Re-run with --skip-log-check if you only want the behavior check.")
        return 1

    if FALLBACK_WARNING in logs:
        print("[error] Received 429, but the API logs show the in-memory fallback warning.")
        print("[error] Redis may be unavailable or misconfigured for the rate limiter path.")
        return 1

    print("[ok] Received 429 and did not detect the in-memory fallback warning in recent API logs.")
    print("[ok] The Redis-backed rate limiter path appears to be active.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
