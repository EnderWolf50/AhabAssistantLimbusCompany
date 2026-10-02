# Mirror UI behaviour (observed)

Facts about the Limbus Company mirror dungeon UI on MuMu (English client, 2560×1440), each confirmed from burst screenshots in a validation run. Coordinates are 2560×1440; code scales them by `cfg.set_win_size / 1440`. Archived captures: `logs/test-runs/*/` (gitignored, main checkout).

## Shop: E.G.O gift power-up (`in_shop.py`, `ego_gift_to_power_up`, `enhance_gifts`)

- **Sort**: AALC clicks the sort button and picks the second option, **Recent** (newest gifts first); the label changes from "By Tier" to "Recent" within ~1 s.
- **List**: 5 columns; 3 full rows visible plus a partial 4th, with a scrollbar. Cell centres x 1367/1550/1733/1917/2100, rows y 515/698/882 (row pitch ~184). The keyword icon AALC matches sits at the cell's bottom right, about (+58, +59) from the cell centre. `enhance_gifts` scrolls the list (drag up ~2 rows from the column gap at x 1641) until the grid stops changing.
- **Tier badge**: top right of the cell. `+` = one orange cross (~36 px wide), `++` = two (~63 px). The selected cell's orange frame also shows up as one orange blob (~44 px). `_is_max_tier` skips `++` gifts.
- **Power-up dialog** (opened by the Power-up button when the gift can be enhanced): an "Enhancement Tier" selector `+` (1814,1022) / `++` (2060,1022), Cancel (1008,1164), Confirm (~1580,1166), and a cost preview top right (e.g. `94 ▸ 44`; region 1880,150–2200,260). Picking `++` from +0 upgrades two tiers in one confirm. When the result would be negative the preview turns red (`44 ▸ -56`), "You need N more Cost" appears and Confirm greys out (same shape, darker; see `docs/agents/recognition-pitfalls.md`).
- **Cannot Enhance toast**: when the gift cannot be enhanced at all (max tier, or not even `+` affordable), Power-up opens **no dialog**; a red "Cannot Enhance / This E.G.O Gift cannot be Enhanced." toast appears top right (template `en/mirror/shop/cannot_enhance_assets.png`).
- **Confirm may be ignored** if clicked while the tier switch is still animating; the dialog then stays open. Only count an upgrade once the dialog has closed.
- The old position-based "already enhanced" list (`enhance_gifts_list`) is only valid within one shop visit; the grid re-sorts as gifts are acquired (#19).

## Shop: buying (`buy_gifts`)

- After buying a gift it moves to the **end** of the goods list with a "Purchased" label and the items after it shift forward one slot; the re-sort is visible ~0.5 s after the purchase. `re_sort_points` predicts exactly this and was verified on two double purchases (#20, closed).
- The ID skill replacement item is the exception: it stays in the first slot when purchased.
- Goods area: 1040,420–2360,1030.

## Shop: refresh

- Keyword refresh: ~1 s after Confirm the panel is closed and goods and money are already updated; the screen is then static. Normal refresh has no panel, and the first one is free (money does not change), so wait for the goods area to change, then freeze.

## Shop: selling

- AALC opens the sell panel on every shop visit and closes it after ~0.4 s if nothing matches the sell list. That is expected.
- Keyword icons on small gifts are easy to confuse when downscaled (a poise gift matched pierce at 0.82). See the irreversible-action rule in `docs/agents/recognition-pitfalls.md`.

## Theme pack page and floor number

- Theme packs sway continuously; this does **not** stall the stable screenshot (the thumbnail barely changes).
- The settings window that opens on every floor is intentional: `get_which_floor` opens it from the gear, counts CLEAR marks, and closes it (~2.4 s per floor). The gear ignores clicks during the page's entry animation; wait for it to settle (`wait_freezes`) and re-click once if the panel did not open.
- After dragging a pack, the floor map's legend appears; selection takes ~3 s end to end now.

## Floor map

- Keyboard navigation plans the whole floor once (YOLO node detection + road templates + Dijkstra; node weights event 1 < shop 2 < battle 4 < boss/focused 6 < risky 7) and then presses one arrow per node. The press shows the node's "Enter" button within ~0.6 s.
- A failed node entry must re-plan; the popped route is otherwise out of sync with the bus.
- First step of a floor: the bus is at the start, so the "click bus, look for Enter" probe is skipped there.

## Events

- A dice-check result screen with a greyed SKIP matched `event/skip_assets.png` at 0.87 and froze the loop when the game itself froze (#17); the frozen-screen restart covers it.
