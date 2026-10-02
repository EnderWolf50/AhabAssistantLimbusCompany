import time
from types import SimpleNamespace

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
