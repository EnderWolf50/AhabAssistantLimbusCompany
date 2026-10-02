#!/bin/sh
# Archive one device test run: archive_run.sh <scratch copy dir> <label>
# -> $AALC_TEST_RUNS/<start time>-<label>/  (default: the main checkout's gitignored logs/test-runs)
# Copies debugLog.log*, the runner stdout, the config used and the COMMIT note. Copy capture folders by hand.
set -e
SRC="$1"; LABEL="$2"
ROOT="${AALC_TEST_RUNS:-D:/Dev/AhabAssistantLimbusCompany/logs/test-runs}"
START=$(sed -n 's/.* \([0-9-]*\) \([0-9:]*\),.*\[AALC\].*/\1-\2/p' "$SRC/run_mirror.out" | head -1 | tr -d ':-' | cut -c1-12)
DEST="$ROOT/${START}-${LABEL}"
mkdir -p "$DEST"
cp "$SRC"/logs/debugLog.log* "$SRC/run_mirror.out" "$SRC/config.yaml" "$DEST/"
[ -f "$SRC/COMMIT" ] && cp "$SRC/COMMIT" "$DEST/"
echo "$DEST"
