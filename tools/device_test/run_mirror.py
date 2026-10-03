# Headless test runner: one normal mirror with the current config, no GUI.
import os, sys, time
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from module.logger import log
from module.logger.my_log import Logger
Logger()
from module.config import cfg

print("CHECK hard_mirror", cfg.hard_mirror, "no_weekly_bonuses", cfg.no_weekly_bonuses, "count", cfg.set_mirror_count,
      "post_input", cfg.post_input_min_wait, "mouse", cfg.mouse_action_interval, flush=True)
if cfg.hard_mirror or cfg.no_weekly_bonuses != 2 or cfg.set_mirror_count != 1:
    sys.exit("ABORT: unsafe mirror flags")
from tasks.base.script_task_scheme import script_task
t0 = time.time()
script_task()
print(f"DONE in {time.time() - t0:.0f}s", flush=True)
