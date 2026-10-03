# Recognition and input pitfalls

Reference for code that takes screenshots, matches templates, OCRs or sends input (`module/automation/automation.py`, `module/ocr/ocr.py`, MuMu input in `module/automation/input_handlers/simulator/mumu_control.py`). Each item cost a real misbehaviour in a mirror run.

## Stale frames

The frame right after an input usually still shows the screen **before** the input (MuMu takes ~180–200 ms to react). Any check made on it can be wrong in a way that looks plausible.

- Replace a fixed `sleep` after an input with `auto.wait_until(condition, timeout)`, and write the condition about a state that does **not** hold before the input: a dialog that appears, a button that disappears, a region that differs from a snapshot taken before the click. "Button X is visible" is only safe when X was absent before the click.
- Keep the old sleep length as the `timeout`, so the worst case is unchanged.
- `find_element` without `take_screenshot=True` reads the last screenshot, which may predate the input. Bugs found this way: `mouse_click_rate` decided on the pre-P frame (#13), the keyword-refresh "did not take effect" retry fired 0.24 s after a click that worked.
- `retry()` runs its popup checks at most once per second (`RETRY_CHECK_INTERVAL`); in between it only refreshes the screenshot if it is stale. Some loops (`back_init_menu`) take no screenshot of their own and see new frames only through `retry()`; a loop that counts attempts must get a fresh frame every iteration, or it burns its count on one frame (that caused a restart loop after a game restart, `9be0abb`).
- Without `screenshot_stable_detect`, `take_screenshot` only enforces `screenshot_interval` since the **last screenshot**, not since the last input; with it, `post_input_min_wait` applies. Write waits that are correct either way.

## Stability waits

- `screenshot_stable_detect` (`_take_stable_screenshot`) waits for the **whole screen** (128×72 thumbnail) to stop changing, capped at `screenshot_interval`. Screens with constant animation (shaking theme packs, battle effects) hit the cap every time.
- `auto.wait_freezes(target=box, time_ms, threshold=0.95, timeout)` is the MaaFramework-style version: wait until one **region** stays unchanged (frame-to-frame `TM_CCOEFF_NORMED >= 0.95`) for `time_ms`. Use it before taking a "before" snapshot or before clicking a button that is visible during its own animation; `click_element(..., pre_wait_freezes=ms)` does the latter around the found element (±100 px approximation).
- Stillness alone cannot tell "already updated" from "not reacted yet". Pair it with a change condition when the screen must change (shop refresh: wait for the goods area to differ, then for it to freeze).

## What counts as an input

`Automation` wraps every `mouse_*` / `key_*` / `input_*` and records `_last_input_time`, which the stable screenshot and `screenshot_is_fresh` use. Adapter methods that do nothing (MuMu `mouse_to_blank`, `mouse_move`, `mouse_scroll`) must be listed in the adapter's `NO_OP_INPUTS`, or every call makes the next screenshot wait ~0.3 s (#12).

## Template matching blind spots

- `TM_CCOEFF_NORMED` ignores brightness: a greyed-out button and an enabled one score the same (power-up Confirm: 0.999 both). Decide enabled/disabled by brightness of the button area (`_power_up_confirm_enabled`: 95th percentile ~206 enabled vs ~56 greyed).
- `recognition_scale` < 1 (0.5 in the test config) raises wrong matches on small icons by ~0.03–0.04 and lowers right ones (charge 0.957 → 0.923). At the default threshold 0.8 this sold a poise gift as pierce (0.82, #21). For anything irreversible (sell, buy, fuse, spending), match with `find_element(..., full_scale=True)` and a threshold of 0.9.
- Thin text also suffers at 0.5: the red "Cannot Enhance" toast scores 0.754 half-scale vs 0.932 full-scale (frames without it ≤ 0.40), so it needs `full_scale=True`. Toasts linger into the next action: one already on screen before the input is not that input's answer.
- Colour frames from any simulator are BGR (MuMu measured; the generic `adb_screenshot` uses `cv2.imdecode`). Go through `Automation._to_rgb()`: `take_color_snapshot()` returns RGB, `get_screenshot_crop()` returns BGR to match the `tasks.sins` table. The node YOLO (`identify_nodes`) is channel-blind: same nodes and classes either way, confidence within 0.03 (#22).
- `click_element` clicks on success; use `find_element` when the intent is only to check. `click_element("battle/turn_assets.png")` used as a "battle ready?" check clicked the TURN icon and blocked acting for 6 s.
- Non-`*_assets.png` templates have no bbox and are searched over the whole frame; `*_assets.png` templates are full-screen images whose non-black area gives the search box. New templates: crop from a real 2560×1440 capture and paste into a black full-size RGBA canvas at the same position; check the score on frames with and without the element before committing.
- Templates are per language (`default/zh_cn`, `default/en`, `default/share`). An `en`-only template silently falls back to the old behaviour on zh_cn; say so in the commit.

## OCR

- `default_rapidocr.yaml` uses `Det.limit_type: min, limit_side_len: 736`: small crops are upscaled to a 736 short side, ~0.5–1 s per call.
- `fast=True` (`ocr.run`, `find_text_element`, `find_language_text`) uses a 320 engine, ~3× faster. Only for calls checked on real crops (#11): main-loop `turn` check, theme pack names, EGO gift white-cotton/Owned, ID skill replacement. Small digits break at 320 (`409` → `60h`), so money and any unverified call stay at 736.
- `_run_ocr_for_text` reuses the result for the same screenshot object + crop + mode.

## MuMu input

- `mouse_drag`: each path point sleeps `point_sleep` (0.02 s default) and the finger is held `hold` before release (0.5 s default); `drag_time` barely matters. Too fast flings the map (0.005 s / 0.2 s threw the bus off screen; 0.01 s / 0.3 s still slid ~20 px). Bus drags use 0.01 s / 0.4 s (`_bus_drag_kwargs`). Re-tune with `tools/device_test/drag_bench.py` on the floor map.
- `mouse_drag_link` (all-defense / chain link) uses 0.1 s per segment.
- Re-clicking a battle skill slot toggles it back to the original skill, so a defense cannot be "redone" by repeating the clicks.

## Frozen game

A frozen game keeps returning identical frames while AALC keeps clicking. `screen_frozen()` (input since the last change and no change for `FROZEN_SCREEN_LIMIT` = 20 s, MaaFramework's default node timeout) makes `retry()` restart the game. Loops that `continue` before their failure counter (the event loop clicking a greyed SKIP, #17) are only protected by this.
