# Memory Auditor for HydraDB

A small Hack Hydra Track 3 demo that stores temporal, source-backed agent-memory claims in HydraDB and audits them for contradictions before an agent acts.

## Problem

Agent memories change across sessions. A flat note or retrieved snippet can look plausible while hiding when it was observed, whether it is still current, or which source supports it. In the sample hospitality workflow, a returning guest has two current room preferences: `quiet` and `near_elevator`. The auditor returns both provenance records and marks the predicate for resolution instead of silently choosing one. A stale `high_floor` preference remains queryable for history.

## Verified behavior

A clean local integration run on 2026-08-14 wrote five claims through HydraDB's HTTP/OpenCypher API and read all five back:

- 4 current claims
- 1 stale claim
- 1 conflict on `prefers_room`, backed by `call-104` and `chat-882`
- 2 passing Python unit checks

The complete audit response is committed as [`demo-output.json`](demo-output.json). No benchmark-accuracy, production-scale, latency, or cost claim is made.

## Architecture

```text
Python CLI (stdlib)
  | seed: CREATE Subject-[:HAS_CLAIM]->Claim
  | audit: MATCH claims by subject key
  v
HydraDB HTTP/OpenCypher API
  v
HydraDB graph store (local object-store persistence in Docker)
  |
  +--> JSON: current_claims / stale_claims / conflicts
```

Each `Claim` records a predicate, object, observation date, source identifier, and current flag. `HAS_CLAIM` connects it to a `Subject`. HydraDB is the durable graph and query layer; without it, this demo has no claim store or audit input.

## Setup and run

Requirements:

- Docker
- Python 3.11+
- `curl`
- Ports `27687`, `28443`, and `29090` available locally

```bash
./start.sh
python3 app.py seed
python3 app.py audit guest:ava
python3 -m unittest -v
```

`start.sh` launches the verified HydraDB image digest `ghcr.io/hydra-db/hydradb@sha256:db78309a233be54662db29744047e985a39b51c45a270d1a1f47c31a62cdb709`, waits up to 30 seconds for `/readyz`, and uses throwaway data under `${TMPDIR:-/tmp}/hydra-memory-auditor`. Set `HYDRA_IMAGE` to test another HydraDB image. The app reads `HYDRA_URL` and `HYDRA_TOKEN` if the defaults are unsuitable.

`./start.sh` resets the named local demo container and its throwaway data before each run. Do not use it against data that must be retained.

## Tests

```bash
python3 -m unittest -v
```

The two unit checks cover OpenCypher string escaping and decoding HydraDB's typed HTTP values. The command sequence above is the integration check.

## Scope and limitations

This is a focused conflict-audit demo, not a general memory platform. It uses `observed` and `current` properties rather than explicit `SUPERSEDES` edges; its conflict rule is “two distinct current objects for one predicate.” It has no LongMemEval/BEAM result, vector-store baseline, explicit natural-language abstention policy, authentication UI, hosted deployment, or measured production cost/latency.

## Submission assets

Form-ready copy, judging mapping, verification notes, and the demo script are in [`submission/SUBMISSION.md`](submission/SUBMISSION.md). Local visual proof and the 75-second captioned demo are in `submission/demo-proof.png` and `submission/hydra-memory-auditor-demo.mp4`.

## Attribution and license

HydraDB is used through its published container and HTTP/OpenCypher API; no HydraDB source is vendored here. Upstream: <https://github.com/hydra-db/hydradb>. The application uses only Python's standard library. Development and packaging were AI-assisted; every functional claim above is backed by the documented local commands.

Licensed under the [MIT License](LICENSE).
