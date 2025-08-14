#!/usr/bin/env bash
set -euo pipefail
python -m txnproc.cli --db transactions.db "$@"
