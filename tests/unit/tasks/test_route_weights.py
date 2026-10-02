import pytest

from tasks.mirror.search_road import RouteGraph, Row

# 2560x1440 坐标：行距 437，bus 在中行 y=730
BUS = (80, 730)
TOP, BOT = 293, 1167


def _first_step(top_class, bottom_class):
    """bus 后一列只有上、下两个节点（都连到 bus），返回路线选的那个。"""
    graph = RouteGraph([[[top_class, (605, TOP)], [bottom_class, (605, BOT)]]], bus_row=Row.MID, bus_position=BUS)
    graph.init_road([(1, Row.MID, Row.TOP), (1, Row.MID, Row.BOTTOM)])
    _, path = graph.find_min_weight_route()
    return path[1].node_class


# 偏好依序：事件 < 商店 < 一般战斗 < 集中/异想体集中 < 精英
@pytest.mark.parametrize(
    "better, worse",
    [
        ("event", "shop"),
        ("shop", "battle"),
        ("battle", "focused_encounter"),
        ("battle", "abnormality_focused_encounter"),
        ("focused_encounter", "risky_encounter"),
    ],
)
def test_node_preference_order(better, worse):
    assert _first_step(better, worse) == better
    assert _first_step(worse, better) == better
