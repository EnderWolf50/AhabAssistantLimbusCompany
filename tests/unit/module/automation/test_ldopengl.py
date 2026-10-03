import pytest

from module.automation.input_handlers.simulator import ldopengl


@pytest.mark.parametrize("port", [16384, 5554, 5556, 7555, 5555 + 66])
def test_ports_outside_ldplayer_range_use_adb(monkeypatch, port):
    # 不在 5555 + 2*index 范围的端口（MuMu 16384、蓝叠等）不应去找 LDPlayer 进程
    monkeypatch.setattr(ldopengl.psutil, "process_iter", lambda *a, **k: pytest.fail("不应搜索进程"))
    assert ldopengl.try_ldopengl(port) is None
