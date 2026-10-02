from types import SimpleNamespace

from module.automation.automation import Automation
from module.automation.input_handlers.simulator.mumu_control import MumuControl


def test_no_op_input_does_not_refresh_last_input_time():
    fake = SimpleNamespace(input_handler=MumuControl, _last_input_time=0.0)
    Automation._mark_input(fake, "mouse_to_blank")
    assert fake._last_input_time == 0.0
    Automation._mark_input(fake, "mouse_click")
    assert fake._last_input_time > 0.0
