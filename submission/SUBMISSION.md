# Hack Hydra Track 3 — local submission package

**Project:** Memory Auditor for HydraDB  
**Track:** Track 3 | Memory + Context Retrieval  
**Package verified:** 2026-08-14T21:12:02Z  
**Official deadline:** 2026-08-20 11:59 PM PT = 2026-08-21 11:59 AM GMT+5  
**State:** complete locally; public repository URL, public video URL, declarations, rules/code-of-conduct agreement, and final form submission are intentionally pending owner approval

## Form-ready answers

### Project Description

Memory Auditor stores temporal, source-backed agent-memory claims in HydraDB and audits them before an agent acts. In a hospitality scenario, it returns four current claims, preserves one stale claim for audit history, and flags one conflicting room-preference predicate with both provenance records instead of silently choosing a value.

### What problem are you solving?

Agent memories change and conflict across sessions. Flat notes or retrieved snippets can surface a plausible value without showing when it was observed, whether it is still current, or which source supports it. An agent needs a reviewable memory layer that exposes provenance, stale facts, and unresolved contradictions before action.

### What did you build?

A standard-library Python CLI that seeds five time-stamped claims, queries them from HydraDB, groups current claims by predicate, and emits agent-consumable JSON containing current claims, stale claims, and distinct current values that need resolution. The sample detects `quiet` versus `near_elevator` as a room-preference conflict and retains the stale `high_floor` claim.

### How does your project use HydraDB?

HydraDB is the core claim store and query layer. The CLI writes `Subject-[:HAS_CLAIM]->Claim` graph patterns through HydraDB's HTTPS/OpenCypher API, then matches all claims for a subject and audits the returned graph records. Each claim carries an observation date, source identifier, and current flag. Without HydraDB, the demo has neither persisted claims nor audit input; it would need a replacement database and query path.

### Tech Stack

Python 3.11 standard library, HydraDB HTTPS/OpenCypher API, Docker, Bash, JSON.

### Team fields

- **Primary contact:** Nurislombek Mahkamjonkhojizoda
- **Team size:** 1, unless the owner corrects this before submission
- **Contribution:** Project owner and submitting participant; implementation and demo packaging were AI-assisted and are disclosed in the README
- **Private email:** enter directly in the live form; do not store in this public package
- **LinkedIn:** enter the owner's verified public profile URL at submission time; no URL was guessed
- **X/Twitter:** optional; leave blank unless the owner chooses to add a verified handle

### URLs

- **Deployed project:** none; this is a reproducible local Docker demo
- **Public GitHub repository:** pending explicit publication approval
- **YouTube demo:** pending explicit upload approval; local source asset is `submission/hydra-memory-auditor-demo.mp4`

### Anything else the judges should know?

This is deliberately narrow and auditable. The verified integration writes and reads five graph claims, returns four current and one stale claim, and identifies one source-backed conflict; two unit checks pass. It does not claim benchmark superiority, production scale, measured cost/latency, or full LongMemEval/BEAM coverage. Revisions are represented by `observed` and `current` properties, not yet by explicit `SUPERSEDES` edges. The conflict rule is distinct current objects under one predicate.

## Architecture / technical summary

```text
app.py seed
  -> HTTPS/OpenCypher CREATE
  -> (Subject)-[:HAS_CLAIM]->(Claim)
  -> HydraDB local object-store-backed graph

app.py audit guest:ava
  -> HTTPS/OpenCypher MATCH by Subject.key
  -> decode HydraDB typed values
  -> partition current/stale
  -> group current claims by predicate
  -> JSON conflict when one predicate has >1 distinct object
```

Claim fields: integer id, predicate, object, observed date, source identifier, and current boolean. The Python layer is intentionally stateless; HydraDB supplies storage and graph retrieval.

## Setup / run

Requirements: Docker, Python 3.11+, `curl`, and free local ports `27687`, `28443`, `29090`.

```bash
cd /home/openclaw/.hermes/workspace/repos/hydra-memory-auditor
./start.sh
python3 app.py seed
python3 app.py audit guest:ava
python3 -m unittest -v
```

For a judge after publication, use the repository clone directory instead of the local absolute path. `start.sh` resets only the named demo container and throwaway `${TMPDIR:-/tmp}/hydra-memory-auditor` data.

## Judging criteria mapping

| Criterion from participant guide | Evidence in this package | Claim boundary |
|---|---|---|
| Technical execution | Reproducible Docker start, real HTTP/OpenCypher writes and reads, typed-value decoder, deterministic JSON audit, two passing unit checks | Small demo; unit checks do not replace an integration suite |
| Use of HydraDB and graph-native approaches | `Subject-[:HAS_CLAIM]->Claim` is written to and queried from HydraDB; provenance and temporal state travel with each claim | No traversal benchmark or explicit `SUPERSEDES` edge yet |
| Product completeness and usability | Four-command setup, CLI output consumable by an agent/front end, committed example output, MIT license, demo asset | Local CLI only; no hosted UI or deployed URL |
| Quality of results | Fresh run: five round-tripped claims, four current, one stale, one conflict with both source records | Scenario result only; no accuracy, latency, scale, or cost benchmark |
| Originality | Pre-action memory audit exposes contradictory current facts and preserved stale history instead of silently selecting a snippet | No comparative study against vector or relational baselines |
| Track 3: time, revisions, missing information, abstention | Observation dates and current/stale partition cover a narrow temporal case | No 30–40-session benchmark; missing-subject output is empty lists, not a first-class natural-language abstention result |

## Verified execution evidence

Fresh integration run against image digest `sha256:db78309a233be54662db29744047e985a39b51c45a270d1a1f47c31a62cdb709`:

```text
./start.sh
readyz=ok

python3 app.py seed
{"seeded_claims": 5, "backend": "HydraDB"}

direct HydraDB round-trip assertion
{'round_tripped': 5, 'current': 4, 'stale': 1, 'ids': [1, 2, 3, 4, 5]}

python3 -m unittest -v
Ran 2 tests in 0.000s
OK
```

`demo-output.json` was separately asserted to contain exactly four current claims, one stale claim, one `prefers_room` conflict with `needs_resolution: true`, the objects `quiet` and `near_elevator`, and non-empty sources on all five claims.

Repository history begins inside the August 12–21 build window. Source, documentation, license, proof card, and captioned demo are committed locally; verify the current head with `git log -1` immediately before publication.

## Claims-safe demo script and storyboard (about 90 seconds)

**0:00–0:15 — Problem**  
“Agent memory changes across sessions. If retrieval hides time and provenance, an agent can act on a plausible but conflicting fact. Memory Auditor makes that conflict reviewable before action.”

**0:15–0:32 — Model and HydraDB**  
“Each claim is a HydraDB node connected to its subject. It stores a predicate, value, observation date, source, and current flag. The Python CLI has no fallback store: seed and audit both go through HydraDB's OpenCypher API.”

**0:32–0:45 — Start and seed**  
Show `./start.sh`, readiness, and `python3 app.py seed`.  
“The clean run starts the pinned HydraDB image and writes five claims.”

**0:45–1:10 — Working audit**  
Show `python3 app.py audit guest:ava` and zoom to the conflict.  
“The audit reads all five back. Four are current. One older high-floor preference stays queryable as stale. Two current room preferences disagree: quiet from call 104 and near elevator from chat 882. The result returns both sources and marks the predicate for resolution.”

**1:10–1:22 — Verification**  
Show `python3 -m unittest -v` and `demo-output.json`.  
“The direct round-trip assertion found IDs one through five, and both unit checks pass.”

**1:22–1:30 — Honest close**  
“This is a focused local demo, not a benchmark claim. Next steps would add explicit revision edges, first-class abstention, and LongMemEval evaluation.”

Visual assets:

1. `submission/demo-proof.png` — screenshot-style verified command/result card.
2. `submission/hydra-memory-auditor-demo.mp4` — locally rendered 75-second captioned demo; must be reviewed before upload.

## Final submission checklist / gate

Ready locally:

- [x] Complete source code
- [x] MIT license
- [x] Clear README, setup/run instructions, HydraDB explanation, dependencies, attribution
- [x] Local demo under three minutes
- [x] Form-ready project answers
- [x] Claims checked against a fresh HydraDB execution
- [x] Participant-authored repository history begins after August 12, 2026

Pending external/owner actions:

- [ ] Confirm team size, verified team email/LinkedIn, contribution wording, and single-submission rule
- [ ] Approve MIT publication and create a public GitHub repository
- [ ] Review then upload the local demo as an accessible YouTube link
- [ ] Verify every public link opens without requesting access
- [ ] Personally review/agree to the Hack Hydra rules and code of conduct
- [ ] Submit the official Google Form

**Executable approval reply:** `HYDRA GO: MIT approved; publish repo, upload demo, and submit Track 3`
