#!/usr/bin/env python3
"""Supabase infrastructure bootstrap helper.

This utility provisions foundational resources that the Instabids
marketplace expects in Supabase.  By default it performs a dry-run and
emits the HTTP calls it would execute.  Pass ``--apply`` to actually
create resources.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from typing import Iterable

BUCKETS = (
    {
        "name": "project-media",
        "public": False,
        "file_size_limit": 50 * 1024 * 1024,  # 50 MiB
        "allowed_mime_types": [
            "image/jpeg",
            "image/png",
            "image/heic",
        ],
        "description": "Raw project photo uploads and SmartScope captures",
    },
    {
        "name": "quote-intake",
        "public": False,
        "file_size_limit": 25 * 1024 * 1024,  # 25 MiB (matches PDF/email limits)
        "allowed_mime_types": [
            "application/pdf",
            "image/jpeg",
            "image/png",
            "image/heic",
            "message/rfc822",
        ],
        "description": "Original quote submissions (PDF, email, photo)",
    },
    {
        "name": "quote-standardized",
        "public": False,
        "file_size_limit": 5 * 1024 * 1024,  # 5 MiB JSON exports
        "allowed_mime_types": ["application/json"],
        "description": "AI-standardized JSON payloads for quote comparisons",
    },
    {
        "name": "contractor-artifacts",
        "public": False,
        "file_size_limit": 50 * 1024 * 1024,
        "allowed_mime_types": [
            "application/pdf",
            "image/jpeg",
            "image/png",
        ],
        "description": "Compliance and credential documents uploaded by contractors",
    },
)

SUPABASE_HEADERS = ("apikey", "Authorization", "Content-Type")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Provision Supabase resources required by the Instabids marketplace.",
    )
    parser.add_argument(
        "resources",
        nargs="+",
        choices=("storage",),
        help="Resource groups to provision. Currently only 'storage' is automated.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually perform the provisioning instead of printing the planned operations.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Force a dry-run even if --apply is passed (useful for validating configuration).",
    )
    return parser


def require_env(var: str) -> str:
    value = os.getenv(var)
    if not value:
        raise SystemExit(f"Missing required environment variable: {var}")
    return value


def supabase_request(
    url: str, key: str, method: str, path: str, body: dict | None
) -> None:
    endpoint = urllib.parse.urljoin(url.rstrip("/") + "/", path.lstrip("/"))
    data = None
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        endpoint, data=data, method=method, headers=headers
    )
    try:
        with urllib.request.urlopen(request) as response:
            # Drain body to avoid ResourceWarning on some Python versions.
            response.read()
    except (
        urllib.error.HTTPError
    ) as exc:  # pragma: no cover - network errors handled at runtime
        if exc.code == 409:
            print(f"  - {path} already exists, skipping")
            return
        message = exc.read().decode("utf-8", errors="ignore")
        raise SystemExit(f"Supabase request failed ({exc.code}): {message}")


def ensure_buckets(base_url: str, service_key: str, *, dry_run: bool) -> None:
    print("Ensuring Supabase storage buckets are present...")
    for bucket in BUCKETS:
        payload = {
            "name": bucket["name"],
            "public": bucket["public"],
            "file_size_limit": bucket["file_size_limit"],
            "allowed_mime_types": bucket["allowed_mime_types"],
        }
        print(
            textwrap.dedent(
                f"""
                Bucket: {bucket['name']}
                  Visibility : {'public' if bucket['public'] else 'private'}
                  Purpose    : {bucket['description']}
                  Size Limit : {bucket['file_size_limit'] // (1024 * 1024)} MiB
                """
            ).strip()
        )
        if dry_run:
            print("  - DRY RUN: would POST /storage/v1/bucket with payload above")
            continue
        supabase_request(base_url, service_key, "POST", "/storage/v1/bucket", payload)
        print("  - Created or confirmed existence")


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.apply and args.dry_run:
        parser.error("--apply and --dry-run cannot be used together")

    # Without --apply we operate in dry-run mode by default.
    dry_run = args.dry_run or not args.apply

    if "storage" in args.resources:
        if dry_run:
            base_url = os.getenv(
                "SUPABASE_URL", "https://lmbpvkfcfhdfaihigfdu.supabase.co"
            )
            service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "<service_role_key>")
        else:
            base_url = require_env("SUPABASE_URL")
            service_key = require_env("SUPABASE_SERVICE_ROLE_KEY")
        ensure_buckets(base_url, service_key, dry_run=dry_run)

    print("\nDone.")
    if dry_run:
        print("(Dry-run mode: no changes were applied.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
