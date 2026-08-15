#!/usr/bin/env bash
set -euo pipefail
ROOT="${TMPDIR:-/tmp}/hydra-memory-auditor"
IMAGE="${HYDRA_IMAGE:-ghcr.io/hydra-db/hydradb@sha256:db78309a233be54662db29744047e985a39b51c45a270d1a1f47c31a62cdb709}"
docker rm -f hydra-memory-auditor >/dev/null 2>&1 || true
rm -rf "$ROOT"
mkdir -p "$ROOT/store" "$ROOT/cache"
printf '%s\n' 'local-development-token-32-bytes' > "$ROOT/auth-token"
docker run -d --name hydra-memory-auditor --user "$(id -u):$(id -g)" \
  -p 27687:7687 -p 28443:8443 -p 29090:9090 \
  -v "$ROOT:/data" \
  -e CLOUD_PROVIDER=local -e LOCAL_PATH=/data/store \
  -e GRAPH_NAMESPACE=memory-audit -e GRAPH_ID=default -e GRAPH_CELL_ID=cell-0 -e GRAPH_CELLS=cell-0 \
  -e GRAPH_NODE_ID=node-0 -e GRAPH_BOLT_NODE_ADDRESSES=node-0=127.0.0.1:7687 \
  -e GRAPH_ADVERTISED_BOLT_ADDR=127.0.0.1:7687 -e GRAPH_DATA_CACHE_DIR=/data/cache \
  -e GRAPH_AUTH_TOKEN_FILE=/data/auth-token -e GRAPH_ALLOW_PLAINTEXT=true -e RUST_MIN_STACK=33554432 \
  "$IMAGE" >/dev/null
for _ in $(seq 1 30); do curl -fsS http://127.0.0.1:29090/readyz >/dev/null && exit 0; sleep 1; done
docker logs hydra-memory-auditor >&2
exit 1
