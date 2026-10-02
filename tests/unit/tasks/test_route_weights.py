from tasks.mirror.search_road import RouteGraph, Row

# 2560x1440 坐标：行距 437，bus 在中行 y=730
BUS = (80, 730)
TOP, MID, BOT = 293, 730, 1167


def _route(columns, connections):
    graph = RouteGraph(columns, bus_row=Row.MID, bus_position=BUS)
    graph.init_road(connections)
    _, path = graph.find_min_weight_route()
    return [node.node_class for node in path]


def test_avoids_risky_even_for_an_extra_event():
    # 上路：事件 → 精英 → 事件；下路：战斗 → 战斗 → 战斗。旧权重下两者总和相同
    columns = [
        [["event", (605, TOP)], ["battle", (605, BOT)]],
        [["risky_encounter", (1115, TOP)], ["battle", (1115, BOT)]],
        [["event", (1628, TOP)], ["battle", (1628, BOT)]],
    ]
    connections = [
        (1, Row.MID, Row.TOP), (1, Row.MID, Row.BOTTOM),
        (2, Row.TOP, Row.TOP), (2, Row.BOTTOM, Row.BOTTOM),
        (3, Row.TOP, Row.TOP), (3, Row.BOTTOM, Row.BOTTOM),
    ]
    assert "risky_encounter" not in _route(columns, connections)


def test_prefers_events_when_nothing_to_avoid():
    columns = [[["event", (605, TOP)], ["battle", (605, BOT)]]]
    connections = [(1, Row.MID, Row.TOP), (1, Row.MID, Row.BOTTOM)]
    assert _route(columns, connections)[1] == "event"
