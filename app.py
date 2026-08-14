#!/usr/bin/env python3
"""Temporal agent-memory audit demo backed by HydraDB."""
import argparse
import json
import os
import urllib.request

BASE = os.getenv("HYDRA_URL", "http://127.0.0.1:28443")
TOKEN = os.getenv("HYDRA_TOKEN", "local-development-token-32-bytes")


def cypher_string(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def query(statement: str) -> list[dict]:
    body = json.dumps({"cell_id": "cell-0", "query": statement}).encode()
    req = urllib.request.Request(
        f"{BASE}/v1/graphs/default/query", body, method="POST",
        headers={"Authorization": f"Bearer {TOKEN}", "X-Graph-Namespace": "memory-audit", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        payload = json.load(response)
    rows = payload.get("rows", payload.get("data", []))
    columns = payload.get("columns", [])
    if rows and isinstance(rows[0], list):
        return [dict(zip(columns, map(decode, row))) for row in rows]
    return [{k: decode(v) for k, v in row.items()} for row in rows]


def decode(value):
    if isinstance(value, dict) and "value" in value and set(value) <= {"type", "value"}:
        return value["value"]
    if isinstance(value, dict):
        return {k: decode(v) for k, v in value.items()}
    if isinstance(value, list):
        return [decode(v) for v in value]
    return value


FACTS = [
    (1, "guest:ava", "prefers_room", "quiet", "2026-08-01", "call-104", True),
    (2, "guest:ava", "prefers_room", "near_elevator", "2026-08-12", "chat-882", True),
    (3, "guest:ava", "arrival", "after_22:00", "2026-08-12", "email-221", True),
    (4, "guest:ava", "needs", "accessible_shower", "2026-08-13", "call-119", True),
    (5, "guest:ava", "prefers_room", "high_floor", "2026-05-01", "email-091", False),
]


def seed() -> None:
    for claim_id, subject, predicate, obj, observed, source, current in FACTS:
        q = f"CREATE (s:Subject {{id: 100, key: {cypher_string(subject)}}})-[:HAS_CLAIM]->(c:Claim {{id: {claim_id}, predicate: {cypher_string(predicate)}, object: {cypher_string(obj)}, observed: {cypher_string(observed)}, source: {cypher_string(source)}, current: {str(current).lower()}}})"
        query(q)
    print(json.dumps({"seeded_claims": len(FACTS), "backend": "HydraDB"}))


def audit(subject: str) -> dict:
    rows = query(
        "MATCH (s:Subject)-[:HAS_CLAIM]->(c:Claim) "
        f"WHERE s.key = {cypher_string(subject)} "
        "RETURN c.id AS id, c.predicate AS predicate, c.object AS object, "
        "c.observed AS observed, c.source AS source, c.current AS current"
    )
    current = [r for r in rows if r.get("current") is True]
    grouped: dict[str, list[dict]] = {}
    for row in current:
        grouped.setdefault(row["predicate"], []).append(row)
    conflicts = [
        {"predicate": predicate, "claims": claims, "needs_resolution": True}
        for predicate, claims in grouped.items()
        if len({c["object"] for c in claims}) > 1
    ]
    return {"subject": subject, "current_claims": current, "conflicts": conflicts,
            "stale_claims": [r for r in rows if r.get("current") is False]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("seed")
    audit_parser = sub.add_parser("audit")
    audit_parser.add_argument("subject", nargs="?", default="guest:ava")
    args = parser.parse_args()
    if args.command == "seed":
        seed()
    else:
        print(json.dumps(audit(args.subject), indent=2))


if __name__ == "__main__":
    main()
