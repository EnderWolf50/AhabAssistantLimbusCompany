from types import SimpleNamespace

from module.automation.automation import Automation


def _fake():
    fake = SimpleNamespace(shots=0)

    def take_screenshot():
        fake.shots += 1
        return object()

    fake.take_screenshot = take_screenshot
    return fake


def test_returns_as_soon_as_condition_holds():
    fake = _fake()
    result = Automation.wait_until(fake, lambda: fake.shots >= 3 and "found", 5)
    assert result == "found"
    assert fake.shots == 3


def test_gives_up_after_timeout():
    fake = _fake()
    assert Automation.wait_until(fake, lambda: None, 0.05) is None
    assert fake.shots >= 1


def test_slow_capture_still_checks_a_frame_taken_after_the_deadline(monkeypatch):
    # LDPlayer 的 adb 截图约 1.7 秒：timeout 1 秒时，第一张图在输入后立刻开始截取，可能还是旧画面；
    # 必须再看一张开始于截止时间之后的图才能放弃
    clock = SimpleNamespace(now=0.0)
    monkeypatch.setattr("module.automation.automation.time.time", lambda: clock.now)
    fake = SimpleNamespace(starts=[])

    def take_screenshot():
        fake.starts.append(clock.now)
        clock.now += 1.7
        return object()

    fake.take_screenshot = take_screenshot
    assert Automation.wait_until(fake, lambda: len(fake.starts) >= 2 and "found", 1) == "found"
