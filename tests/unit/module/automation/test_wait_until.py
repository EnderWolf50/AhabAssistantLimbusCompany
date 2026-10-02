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
