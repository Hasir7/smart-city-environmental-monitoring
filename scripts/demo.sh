#!/usr/bin/env bash
set -euo pipefail

curl -X POST "http://localhost:8001/simulate?count=30"
echo
curl "http://localhost:8000/metrics/summary"
echo
