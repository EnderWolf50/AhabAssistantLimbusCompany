from types import SimpleNamespace

import numpy as np
from PIL import Image

from module.automation.automation import Automation


def _fake(frames):
    """依序回传 frames 中的画面，用完后一直回传最后一张。"""
    fake = SimpleNamespace(screenshot=None, shots=0)

    def take_screenshot():
        fake.screenshot = frames[min(fake.shots, len(frames) - 1)]
        fake.shots += 1
        return fake.screenshot

    fake.take_screenshot = take_screenshot
    return fake


def _frame(seed):
    rng = np.random.default_rng(seed)
    return Image.fromarray(rng.integers(0, 255, (72, 128), dtype=np.uint8))


def test_returns_once_the_target_stops_changing():
    fake = _fake([_frame(1), _frame(2), _frame(3), _frame(3)])
    assert Automation.wait_freezes(fake, target=(0, 0, 64, 36), time_ms=0, timeout=5)
    assert fake.shots == 4


def test_gives_up_while_still_changing():
    frames = [_frame(i) for i in range(1000)]
    assert not Automation.wait_freezes(_fake(frames), time_ms=0, timeout=0.05)
