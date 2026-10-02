#!/bin/sh
# cap.sh <log> <grep -E pattern> <out dir> <seconds> <times>
# Each time the pattern count in the log grows, screencap repeatedly for <seconds> (read-only); repeat <times> times.
LOG="$1"; PAT="$2"; OUT="$3"; SECS="$4"; TIMES="$5"
mkdir -p "$OUT"
until [ -f "$LOG" ]; do sleep 1; done
k=0
while [ $k -lt "$TIMES" ]; do
  n0=$(grep -cE "$PAT" "$LOG")
  while [ "$(grep -cE "$PAT" "$LOG")" -le "$n0" ]; do sleep 0.3; done
  end=$(( $(date +%s) + SECS )); i=0
  while [ "$(date +%s)" -lt "$end" ]; do
    adb -s 127.0.0.1:16384 exec-out screencap -p > "$OUT/$(date +%H%M%S)_${k}_$i.png"; i=$((i+1))
  done
  echo "burst $k: $i shots"; k=$((k+1))
done
