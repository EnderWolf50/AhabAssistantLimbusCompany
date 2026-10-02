# PROTOTYPE: throwaway. Run from a scratch AALC copy while the game shows a mirror floor map.
# Drags the bus to the left edge with different (per-point sleep, hold before release) settings, measures time,
# where the bus ends up, and how far the map keeps sliding after release; drags it back between trials.
# Only drags the map view; never taps a node.
import time, statistics as st
from module.config import cfg
from module.automation import auto
from module.automation.input_handlers.simulator import insert_swipe
from module.automation.input_handlers.simulator.mumu_control import MumuControl
from utils.path_manager import path_manager

MumuControl(instance_number=0)
auto.init_input()
path_manager.initialize_paths()
auto.clear_img_cache()
dev = MumuControl.connection_device
BUS = "mirror/mybus_default_distance.png"
TARGET = (80, 690)


def bus():
    return auto.find_element(BUS, take_screenshot=True)


def drag(p0, p1, point_sleep, hold):
    t = time.perf_counter()
    dev.down(*p0)
    for p in insert_swipe(p0=p0, p3=p1):
        dev.down(*p)
        time.sleep(point_sleep)
    time.sleep(hold)
    dev.up()
    return time.perf_counter() - t


def settle():
    """bus position right after release, then after the map stops (max 3 s)."""
    first = bus()
    last, t0 = first, time.time()
    while time.time() - t0 < 3:
        cur = bus()
        if cur and last and abs(cur[0] - last[0]) < 3 and abs(cur[1] - last[1]) < 3:
            return first, cur
        last = cur
    return first, last


start = bus()
assert start, "bus not found - is the game on the mirror map?"
print("start", start)
variants = [(0.02, 0.5), (0.01, 0.3), (0.005, 0.2), (0.005, 0.1), (0.0, 0.1)]
for ps, hold in variants:
    res = []
    for _ in range(2):
        b = bus()
        dur = drag((int(b[0]), int(b[1])), TARGET, ps, hold)
        first, final = settle()
        slide = abs(final[0] - first[0]) + abs(final[1] - first[1]) if first and final else None
        err = abs(final[0] - TARGET[0]) + abs(final[1] - TARGET[1]) if final else None
        res.append((dur, err, slide))
        print(f"sleep={ps} hold={hold}: drag {dur:.2f}s  final={final} err={err} slide_after_release={slide}", flush=True)
        b = bus()
        drag((int(b[0]), int(b[1])), (int(start[0]), int(start[1])), 0.02, 0.5)  # back to start, baseline
        settle()
print("done")
