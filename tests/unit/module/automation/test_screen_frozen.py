import time
from types import SimpleNamespace

import numpy as np
from PIL import Image

from module.automation.automation import Automation


def _fake(last_change_ago, last_input_ago):
    now = time.time()
    return SimpleNamespace(
        FROZEN_SCREEN_LIMIT=Automation.FROZEN_SCREEN_LIMIT,
        _last_screen_change=now - last_change_ago,
        _last_input_time=now - last_input_ago,
    )


def test_frozen_when_inputs_keep_coming_but_screen_never_changes():
    assert Automation.screen_frozen(_fake(last_change_ago=60, last_input_ago=1))


def test_not_frozen_without_input_after_the_last_change():
    # 例如等待战斗动画、暂停中：画面不变但没有输入
    assert not Automation.screen_frozen(_fake(last_change_ago=60, last_input_ago=61))


def test_not_frozen_within_limit():
    assert not Automation.screen_frozen(_fake(last_change_ago=10, last_input_ago=1))


def _changed(a, b):
    fake = SimpleNamespace(_thumbnail=Automation._thumbnail)
    Automation._watch_frozen(fake, Image.fromarray(a.astype(np.uint8)))
    fake._last_screen_change = None
    Automation._watch_frozen(fake, Image.fromarray(b.astype(np.uint8)))
    return fake._last_screen_change is not None


def test_small_progress_bar_step_counts_as_change():
    # 1920x1080 读取画面：只有一格进度条（约 30x40）由暗变亮，整张图的平均差极小
    a = np.full((1080, 1920), 20)
    b = a.copy()
    b[990:1030, 1440:1470] = 200
    assert _changed(a, b)


def test_identical_frames_are_no_change():
    a = np.full((1080, 1920), 20)
    assert not _changed(a, a.copy())
