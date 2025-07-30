#!/usr/bin/env bash
set -euo pipefail

echo "=== Frontend smoke test ==="
curl -sf http://lugx.local/ | grep -q "<title>Lugx Gaming</title>"
echo "→ Frontend OK"

echo "=== Analytics smoke test ==="
curl -sf -X POST http://lugx.local/analytics/track \
     -H "Content-Type: application/json" \
     -d '{"eventType":"ci_test","page":"/ci"}'
echo "→ Analytics POST OK"

echo "=== ClickHouse data check ==="
kubectl exec deploy/clickhouse -- \
  clickhouse-client -q "SELECT count() FROM lugx.web_events" \
  | grep -Eq '^[0-9]+$'
echo "→ ClickHouse OK"

echo "=== Game‑service smoke test ==="
curl -sf http://lugx.local/games
echo "→ Game service OK"

echo "=== Order‑service smoke test ==="
curl -sf http://lugx.local/orders
echo "→ Order service OK"

echo "All integration tests passed!"
