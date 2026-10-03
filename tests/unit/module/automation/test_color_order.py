from types import SimpleNamespace

import numpy as np
import pytest
from PIL import Image

from module.automation.automation import Automation
from module.config import cfg

RED = (255, 0, 0)  # 游戏画面上的真实红色（RGB）


def _frame(simulator):
    # PC 截图是 RGB；模拟器截图的数组是 BGR（MuMu IPC、adb 的 cv2.imdecode）
    pixel = RED[::-1] if simulator else RED
    return Image.fromarray(np.full((4, 4, 3), pixel, dtype=np.uint8))


@pytest.mark.parametrize("simulator", [False, True])
def test_colour_helpers_agree_on_channel_order(monkeypatch, simulator):
    monkeypatch.setattr(cfg, "simulator", simulator, raising=False)
    fake = SimpleNamespace(take_screenshot=lambda gray: None, screenshot=_frame(simulator), _to_rgb=Automation._to_rgb)

    assert tuple(Automation._to_rgb(fake.screenshot)[0, 0]) == RED
    # find_skill3 的颜色表（tasks.sins）是 BGR
    assert tuple(Automation.get_screenshot_crop(fake, (0, 0, 2, 2))[0, 0]) == RED[::-1]
