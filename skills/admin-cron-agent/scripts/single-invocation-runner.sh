#!/bin/bash
# single-invocation-runner.sh
# Runs build → start → POST → kill in one shell so the server survives.
# Usage: bash single-invocation-runner.sh /tmp/data.json
#
# Env overrides:
#   APP_DIR      - app root (default: /home/user/workspace/family-admin)
#   API_PORT     - port    (default: 5000)
#   API_ENDPOINT - path    (default: /api/inbox/scan)

set -e

DATA_FILE="${1:-/tmp/data.json}"
APP_DIR="${APP_DIR:-/home/user/workspace/family-admin}"
API_PORT="${API_PORT:-5000}"
API_ENDPOINT="${API_ENDPOINT:-/api/inbox/scan}"
BASE_URL="http://localhost:${API_PORT}"

echo "[runner] DATA_FILE=$DATA_FILE  PORT=$API_PORT"

EMAIL_COUNT=$(python3 -c "import json; print(len(json.load(open('$DATA_FILE'))))" 2>/dev/null || echo 0)
if [ "$EMAIL_COUNT" -eq 0 ]; then
  echo '{"total_extracted":0,"results":[]}' > /tmp/results.json
  echo "[runner] No items — done."
  exit 0
fi

# Clear port
fuser -k "${API_PORT}/tcp" 2>/dev/null || true
sleep 1

# Build if needed
[ -d "${APP_DIR}/dist" ] || (cd "${APP_DIR}" && npm run build 2>&1 | tail -5)

# Start server
cd "${APP_DIR}"
NODE_ENV=production node dist/index.cjs &
SERVER_PID=$!

# Wait for readiness
for i in $(seq 1 30); do
  curl -s "${BASE_URL}/api/health" > /dev/null 2>&1 && echo "[runner] Ready (${i}s)" && break
  sleep 1
done

# POST items
python3 - "$DATA_FILE" "$BASE_URL" "$API_ENDPOINT" <<'PYEOF'
import json, sys, urllib.request
data_file, base_url, endpoint = sys.argv[1], sys.argv[2], sys.argv[3]
items = json.load(open(data_file))
results = []
total = 0
for item in items:
    req = urllib.request.Request(f"{base_url}{endpoint}",
          data=json.dumps(item).encode(),
          headers={"Content-Type":"application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.loads(r.read())
            n = d.get("extractedCount", 0); total += n
            results.append({"subject": item.get("subject",""), "status": "extracted" if n>0 else "skipped", "count": n})
    except Exception as e:
        results.append({"subject": item.get("subject",""), "status": "error", "count": 0, "error": str(e)})
json.dump({"total_extracted": total, "results": results}, open("/tmp/results.json","w"))
print(f"[runner] Done. total_extracted={total}")
PYEOF

kill $SERVER_PID 2>/dev/null || true
echo "[runner] Server stopped."
