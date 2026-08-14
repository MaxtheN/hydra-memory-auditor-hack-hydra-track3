# Memory Auditor for HydraDB

A small Track 3 demo: an AI agent stores temporal claims with provenance in HydraDB, then audits current memory for contradictions before acting.

The sample hospitality workflow catches a real failure mode: a returning guest has two current room preferences (`quiet` and `near_elevator`). Instead of silently picking one, the agent returns both source records and marks the predicate for resolution. Superseded claims remain queryable for audit history.

## Run

Requires Docker and Python 3.11+.

```bash
./start.sh
python3 app.py seed
python3 app.py audit guest:ava
python3 -m unittest -v
```

HydraDB is the durable graph layer, queried through its HTTP/OpenCypher API. The application itself uses only Python's standard library.

## Why a graph

Memory is not a flat note. Claims belong to subjects, come from sources, change over time, and can disagree. The same shape extends naturally to `SUPPORTED_BY`, `SUPERSEDES`, and multi-agent provenance edges without copying context into prompts.

## Demo output

The audit returns current claims, stale claims, and source-backed conflicts as JSON, making it directly consumable by an agent approval step or a front end.
