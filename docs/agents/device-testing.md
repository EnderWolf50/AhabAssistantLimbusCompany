# Device testing: validating a change with a real mirror run

How to validate an AALC change end to end on the MuMu emulator, headless and from source, without touching the user's installed AALC. Scripts referenced here live in `tools/device_test/`.

## Hard rules (the user set these; never trade them for speed)

- **Weekly bonuses are for hard mirrors only.** Every validation run is a **normal** mirror with `no_weekly_bonuses: 2` (the GUI resets a plain `true`/`1`; `2` survives). `run_mirror.py` prints a `CHECK ...` line and refuses to start unless `hard_mirror` is false, `no_weekly_bonuses == 2` and `set_mirror_count == 1`. Read that line before anything else; if it is wrong, stop.
- Never buy, sell, enhance or press "Halt Exploration" in a bench or probe script. Benches only open/close panels or drag the map view. (The mirror run itself buys/sells/enhances through AALC's own logic; that is the thing under test.)
- Only one Limbus client at a time: never run Steam Limbus while the MuMu game is running.
- Before shutting the MuMu instance down, send Home (`adb -s 127.0.0.1:16384 shell input keyevent 3`) and wait ~5 s, or game settings are lost.
- Ask before pushing to anything other than the working branch, merging, or commenting on upstream.

## Steps

1. **Commit the code under test** on the work branch; note the short hash.
2. **Make a scratch copy** of the working tree outside the repo (the job temp dir), so a running test is never affected by later edits:
   `uv run --frozen python tools/device_test/mkcopy.py . <scratch>` → `cd <scratch>` → `uv sync --frozen --no-dev`.
   Write the commit hash into `<scratch>/COMMIT`.
3. **Config**: copy the previous scratch copy's `config.yaml` (or the user's `D:\Tools\AALC\config.yaml`) and set, in the copy only: `simulator: true`, `mumu_instance_number: 0`, `set_mirror_count: 1`, `hard_mirror: false`, `no_weekly_bonuses: 2`, plus the speed settings under test (`screenshot_stable_detect`, `post_input_min_wait`, `mouse_action_interval`, `recognition_scale`). Copy `tools/device_test/run_mirror.py` in.
4. **Check the device**: `adb connect 127.0.0.1:16384` (the connection drops after every AALC run), take a screencap and confirm the game is on the main menu or inside the mirror to be resumed.
5. **Start** from `<scratch>`: `.venv\Scripts\python.exe -u run_mirror.py *> run_mirror.out` in the background. Confirm the `CHECK` line.
6. **Watch** `<scratch>/logs/debugLog.log` with a filtered tail (errors, `已完成`, restart/stuck lines, plus whatever the change is about); it is plain UTF-8. `run_mirror.out` only for `CHECK` / `DONE`: started from Git Bash its Chinese comes out as `\uXXXX` escapes, so Chinese patterns silently never match. Optional burst captures: `sh tools/device_test/cap.sh <scratch>/logs/debugLog.log "<log pattern>" <out dir> <seconds> <times>` screencaps for N seconds each time the pattern appears (read-only). Useful patterns: `开始执行饰品出售模块`, `开始执行饰品升级模块`, `开始购买本体系饰品`, `refresh_keyword_assets.png|refresh_assets.png`.
7. **Ask the user not to touch the MuMu window** during the run. Switching to it broke drags twice (all-defense turns did not register).
8. **Archive** when `DONE` appears: `sh tools/device_test/archive_run.sh <scratch> <label>` (→ `logs/test-runs/<start>-<label>/`, gitignored), then copy capture folders into it. AALC rotates `debugLog.log` (5 MB × 10) and the scratch copy dies with the job.
9. **Compare** with earlier archives (see `docs/agents/perf-measurement.md`) and check correctness from captures before calling the change done.

The step is done when the run reached `已完成 1 次镜牢`, the archive folder exists with the log and config, and every behaviour the change touched has been checked in the log or a capture.

## Stopping at a specific screen

To run a bench on a screen the mirror reaches (e.g. the floor map for `drag_bench.py`), watch the log for the marker (`结束执行 选择镜牢主题包` = on the map) and kill the runner process right away (match `*<scratch>*run_mirror.py*` in the command line). Restarting the runner later resumes the mirror; move the old `run_mirror.out` aside first so `cap.sh` counts start fresh.

## Known environment problems

- **MuMu/Limbus freezes** happened twice in one run (identical screencaps 15 s apart, game process alive). Since `3af2640`/`c72c18d` AALC restarts the game after 20 s of no screen change under input; before that the user restarted by hand and AALC resumed.
- `adb devices` empty after a run → `adb connect 127.0.0.1:16384`.
- **LDPlayer 9** (`simulator_type: 10`, port 5555, `cap.sh` with `ADB_SERIAL=127.0.0.1:5555`): AALC captures through `ldopengl64.dll` (~10 ms; adb screencap ~1.7 s). The user found the game itself runs slowly there and prefers MuMu. A device that has never opened the Mirror Dungeon shows a first-visit guide (closed with Esc since `a1faff4`). Its memory setting is 6 GB; with WSL and browsers open the host has run out of memory and Claude Code reaped the runner twice.
- Shell hooks in this repo refuse compound commands that mix git/gh with variables or pipes from a worktree session; run them as plain single commands.
