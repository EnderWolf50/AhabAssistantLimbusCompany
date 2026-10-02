# Battle notes

Observed game behaviour and AALC pitfalls in `tasks/battle/battle.py`. Read before changing how turns are started, defended or polled.

## Starting a turn

- Every way of acting (P+Enter, all-defense drag, chain link, win-rate-card click) is followed by `_wait_turn_started()`: poll for `battle/pause_assets.png` (it only shows while a turn plays) for up to 3 s. Without it the next loop iteration sees the pre-turn frame and acts again (29 of 59 P+Enter turns were doubled, #13).
- `mouse_click_rate` (fallback: click the win-rate card + right gear when P+Enter does not start a turn) is set only when `_wait_turn_started()` fails, never from a stale frame.
- Only **look** for the TURN icon (`find_element("battle/turn_assets.png")`). Clicking it blocked the defense drag and P+Enter for ~6 s; the next click unblocked it (#14 follow-up, `f709a1f`).

## All-defense and solo-defense turns

- `_defense_this_round()` clicks every skill slot (switches it to its defense skill), then drags a link from the left gear through all slots to the right gear. Re-clicking a slot toggles it back, so a failed defense is not retried; it falls back to P+Enter (attacks instead).
- The solo-defense quota (`DefenseForSoloState`, 小指良单通连续防御, 5 turns per mirror) is consumed only after the turn actually started (#18). A failed defense keeps the turn for later.
- Known cause of failed defenses: the user switching to the MuMu window (Alt+Tab, mouse over the emulator) while the drag is injected. It happened in two runs; the user considers the P+Enter fallback acceptable. Keep the window untouched during validation runs.
- Timings on MuMu after #9: ~4.1–4.7 s from the selection screen to the turn running (was ~10 s).

## Polling while a turn plays and between screens

- While the pause button is visible: `sleep(0.5)` per check. Between screens (nothing matched): `sleep(0.3)`. The old waits grew with every failed match (`_update_wait_time`, up to 2×3 s) and were removed (#14).
- The "click screen centre to skip the announcer" click is rate-limited to once per second; at the faster loop it would otherwise fire constantly and risks opening the status page.
- `fail_count` grows with loop iterations, so branches gated on it (`fail_count >= 5`) are reached much earlier at 0.3 s polling. Anything behind such a gate must be harmless to run early (this is how the TURN click surfaced).

## Measuring battle speed

Whole-battle duration depends on enemies and luck; compare AALC's own action latencies instead (see `docs/agents/perf-measurement.md`): turn end → selection screen noticed (2.7 s median after #14, was 4–5 s) and action → turn running (~1.8 s).
