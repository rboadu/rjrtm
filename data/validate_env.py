#!/usr/bin/env python3
"""
Validate presence of DB-related environment variables for local runs.

Usage:
    python -m data.validate_env
or:
    python data/validate_env.py
"""
import os
import sys

CANDIDATES = [
    "DATABASE_URL",
    "MONGO_URI",
    "DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD",
]

def main() -> int:
    missing = [k for k in CANDIDATES if os.environ.get(k) in (None, "")]
    present = [k for k in CANDIDATES if k not in missing]

    print("== data/validate_env ==", file=sys.stderr)
    if present:
        print("Found:", ", ".join(present))
    else:
        print("Found: (none)")

    if any(os.environ.get(k) for k in ("DATABASE_URL", "MONGO_URI")):
        print("Status: OK (single URL present)")
        return 0

    split = ("DB_HOST", "DB_PORT", "DB_NAME")
    if any(os.environ.get(k) for k in split):
        print("Status: OK (partial split vars present)")
        return 0

    print("Status: WARN (no DB env vars found)")
    print("Tip: set DATABASE_URL or MONGO_URI, or split variables (DB_HOST/DB_PORT/DB_NAME...).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
