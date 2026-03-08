#!/usr/bin/env python3
"""Smoke-test the public + verified intent membrane through steward-protocol."""

import argparse
import json
import sys
import time
import uuid
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from vibe_core.steward.crypto import generate_keys, sign_content


def _request_json(base_url: str, path: str, *, method: str = "GET", payload: dict | None = None, headers: dict | None = None, timeout: float = 10.0) -> tuple[int, dict]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(f"{base_url.rstrip('/')}{path}", data=data, method=method)
    request.add_header("Content-Type", "application/json")
    for key, value in (headers or {}).items():
        request.add_header(key, value)
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        payload = json.loads(body) if body else {}
        return exc.code, payload


def _expect(status: int, payload: dict, expected: int, label: str) -> None:
    if status != expected:
        raise SystemExit(f"{label} failed: expected {expected}, got {status}, payload={json.dumps(payload)}")


def _intent_fields(*, intent_type: str, title: str, description: str, repo: str, space_id: str, requested_by_handle: str) -> dict:
    return {
        "intent_type": intent_type,
        "title": title,
        "description": description,
        "repo": repo,
        "city_id": "",
        "space_id": space_id,
        "slot_id": "",
        "lineage_id": "",
        "discussion_id": "",
        "requested_by_handle": requested_by_handle,
        "linked_issue_url": "",
        "linked_pr_url": "",
        "labels": {"smoke": "true"},
    }


def _sign_payload(payload: dict, private_key_pem: str, *, timestamp: int) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sign_content(f"{canonical}:{timestamp}", private_key_pem)


def run_public(base_url: str, *, timeout: float, repo: str, space_id: str, requested_by_handle: str) -> dict:
    suffix = uuid.uuid4().hex[:8]
    create_payload = _intent_fields(
        intent_type="request_issue",
        title=f"Public smoke {suffix}",
        description="Public membrane smoke test.",
        repo=repo,
        space_id=space_id,
        requested_by_handle=requested_by_handle,
    )
    status, created = _request_json(base_url, "/v1/public-intents", method="POST", payload=create_payload, timeout=timeout)
    _expect(status, created, 200, "public create")
    intent_id = created["data"]["intent"]["intent_id"]
    status, fetched = _request_json(base_url, f"/v1/public-intents/{intent_id}", timeout=timeout)
    _expect(status, fetched, 200, "public read")
    return {"intent_id": intent_id, "status": fetched["data"]["intent"]["status"]}


def run_verified(base_url: str, *, api_key: str, timeout: float, repo: str, space_id: str, requested_by_handle: str, agent_id: str) -> dict:
    private_key_pem, public_key_pem = generate_keys()
    timestamp = int(time.time())
    create_fields = _intent_fields(
        intent_type="request_slot",
        title=f"Verified smoke {uuid.uuid4().hex[:8]}",
        description="Verified membrane smoke test.",
        repo=repo,
        space_id=space_id,
        requested_by_handle=requested_by_handle,
    )
    create_payload = {
        **create_fields,
        "agent_id": agent_id,
        "signature": _sign_payload(create_fields, private_key_pem, timestamp=timestamp),
        "public_key": public_key_pem,
        "timestamp": timestamp,
    }
    headers = {"x-api-key": api_key}
    status, created = _request_json(base_url, "/v1/intents", method="POST", payload=create_payload, headers=headers, timeout=timeout)
    _expect(status, created, 200, "verified create")
    intent = created["data"]["intent"]
    expected_subject = f"verified_agent:{agent_id}"
    if intent.get("requested_by_subject_id") != expected_subject:
        raise SystemExit(f"verified create stored wrong subject: {intent.get('requested_by_subject_id')} != {expected_subject}")
    intent_id = intent["intent_id"]

    timestamp = int(time.time())
    status_fields = {"intent_id": intent_id}
    status_payload = {
        **status_fields,
        "agent_id": agent_id,
        "signature": _sign_payload(status_fields, private_key_pem, timestamp=timestamp),
        "public_key": public_key_pem,
        "timestamp": timestamp,
    }
    status_code, fetched = _request_json(base_url, "/v1/intents/status", method="POST", payload=status_payload, headers=headers, timeout=timeout)
    _expect(status_code, fetched, 200, "verified read")
    fetched_intent = fetched["data"]["intent"]
    if fetched_intent.get("requested_by_subject_id") != expected_subject:
        raise SystemExit(f"verified read stored wrong subject: {fetched_intent.get('requested_by_subject_id')} != {expected_subject}")
    return {"intent_id": intent_id, "status": fetched_intent["status"], "requested_by_subject_id": fetched_intent["requested_by_subject_id"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True, help="Steward-protocol base URL, e.g. http://127.0.0.1:8000")
    parser.add_argument("--api-key", default="", help="Required for verified flow")
    parser.add_argument("--repo", default="org/city-smoke")
    parser.add_argument("--space-id", default="space:city-smoke:moltbook_assistant")
    parser.add_argument("--requested-by-handle", default="smoke")
    parser.add_argument("--agent-id", default="smoke_agent")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--skip-public", action="store_true")
    parser.add_argument("--skip-verified", action="store_true")
    args = parser.parse_args()

    if args.skip_public and args.skip_verified:
        parser.error("at least one flow must be enabled")
    if not args.skip_verified and not args.api_key:
        parser.error("--api-key is required unless --skip-verified is used")

    summary: dict[str, dict] = {}
    if not args.skip_public:
        summary["public"] = run_public(args.base_url, timeout=args.timeout, repo=args.repo, space_id=args.space_id, requested_by_handle=args.requested_by_handle)
    if not args.skip_verified:
        summary["verified"] = run_verified(
            args.base_url,
            api_key=args.api_key,
            timeout=args.timeout,
            repo=args.repo,
            space_id=args.space_id,
            requested_by_handle=args.requested_by_handle,
            agent_id=args.agent_id,
        )

    print(json.dumps({"status": "ok", "base_url": args.base_url, "summary": summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())