# Measuring speed

How to tell whether a change made AALC faster without fooling yourself. Inputs are archived run logs (`logs/test-runs/*/run_mirror.out`, see `docs/agents/device-testing.md`).

## Compare actions, not totals

A whole mirror, and especially a battle, varies run to run with enemies, events and shop luck (battle medians moved 60 → 68 s between two runs with faster AALC actions). Judge a change by the latency of AALC's own actions:

- `tools/device_test/compare.py <run_mirror.out>...`: per-step durations from the `结束执行 <step> 耗时` lines (shop, theme pack, pathfinding, battle), and doubled P+Enter turns (pairs < 1.5 s apart; should be 0).
- `tools/device_test/action_cmp.py <run_mirror.out>...`: battle latencies. A = last pause button seen → selection screen seen (AALC noticing a turn ended); B = selection screen → pause button (AALC acting until the turn runs). Baseline before the speed work: A 4.2 s / B 1.8 s; after #14: A 2.7 s / B 1.8 s.
- For one screen, reconstruct a timeline from the log: every click line (`点击位置`) plus template matches ≥ 0.8, with the gap to the previous event. Gaps of ~1.0 s, ~3.0 s or 0.5 s repeating are fixed sleeps; gaps that stop at 0.85 s are the stable-screenshot cap.

## Reading the log

- Lines are `[LEVEL] date time,ms [AALC] file:line: message`. Template matches log `目标图片：<path>, 路径: <lang dir>, 相似度：<score>, 目标位置：(x, y)` for every attempt, including misses; filter by score.
- Line numbers in old logs refer to the code at that run's `COMMIT`, not the current tree.
- `retry.py` lines are background noise from every loop; drop them when reading timelines.
- `[RapidOCR] ... The text detection result is empty` is harmless noise.

## Results so far (normal mirror, MuMu)

| | before (1857 s total) | after batch 2 |
|---|---|---|
| shop (median) | 45 s | 26–30 s |
| theme pack selection | 6 s | 3 s |
| pathfinding (30 steps) | 45 s | 20 s |
| solo-defense turn | ~10 s | ~4.4 s |
| OCR, whole run | 91 s | ~33 s if all calls used 320 (only validated calls do) |
