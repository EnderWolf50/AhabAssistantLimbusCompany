# AALC domain context

AALC automates the gacha game **Limbus Company** (ProjectMoon) on PC (Steam) or an Android emulator (MuMu recommended). This file maps the game's concepts to AALC's code and log vocabulary. Code comments and logs are Simplified Chinese; the terms below give the English game name, the Chinese used in logs/UI, and where AALC handles it. Timing: each `@begin_and_finish_time_log(task_name=...)` step logs `开始执行 <name>` / `结束执行 <name> 耗时:hh:mm:ss`.

## One script run (`tasks/base/script_task_scheme.py: script_task`)

1. `init_game()`: start or attach to the game (MuMu: `MumuControl`, PC: window handle), set up input.
2. If the game is mid-battle, finish that battle first.
3. Then, each if enabled in config, in this order:
   - **Daily tasks** (`daily_task`): Luxcavation runs. **EXP Luxcavation** (经验本, `一次经验本`) and **Thread Luxcavation** (纽本, `一次纽本`).
   - **Rewards** (`get_reward`): daily/weekly missions (`收取日常/周常`) and the mailbox (`收取邮箱`).
   - **Buy enkephalin** (`buy_enkephalin`): **Lunacy → Enkephalin** (`狂气换体`).
   - **Mirror Dungeon** (`mirror`): `Mirror_task()` runs `set_mirror_count` mirrors, rotating through the selected teams.
4. After-completion actions (`after_completion_actions`: exit game / emulator / AALC, power action).

`retry_monitor` runs in a background thread for the whole run and clicks the server "Retry" popup.

## Resources

- **Enkephalin** (体力): stamina, regenerates over time. **Enkephalin Module** (饼, 脑啡肽模组): made from enkephalin (`体力换饼`, `make_enkephalin_module.py`); spent to claim mirror rewards.
- **Lunacy** (狂气): premium currency; can buy enkephalin.
- **Cost** (shop money inside a mirror, the ⊛ number): earned in the mirror, spent in its shops; read by OCR in `InShop._get_cost`.

## Mirror Dungeon run (`tasks/mirror/mirror.py: Mirror.run`)

A **mirror** (镜牢, Mirror Dungeon; current season "Mirror of Names and Spiders") is a roguelike run of **5 floors**. Normal (普牢) vs **Hard** (困牢, `hard_mirror`). One run, in order:

1. **Enter** from Drive → Mirror Dungeons; pick the **team** (`寻找队伍`, `team_formation.py`), confirm level, **Dreaming Star / starlight** bonuses (`dreaming_star`, spend starlight on buffs), **starting E.G.O gifts** and **observe E.G.O gift** (pick by keyword).
2. Per floor:
   - **Theme pack** (主题包, 卡包) selection (`选择镜牢主题包`, `select_theme_pack.py`): drag one of the offered packs; chosen by OCR'd name and per-pack weights (`theme_list`). Before it AALC opens the settings panel to read the floor number (`get_which_floor`) and switches difficulty if needed.
   - **Floor map** (`镜牢寻路`, `search_road.py`): a bus moves through columns of **nodes**: battle (`一次战斗`), event, shop (`镜牢商店`), focused/risky encounters, abnormality, boss. AALC plans a route once per floor (node weights) and enters nodes by keyboard.
   - **Encounter reward cards** after battles (`镜牢获取奖励卡`, `reward_card.py`) and **E.G.O gift choices** (`acquire_ego_gift`).
   - **Events** (`event_handling.py`): text choices and **checks** (dice roll vs threshold with a chosen sinner).
3. After floor 5's boss: **claim rewards** (`claim_reward`), paying enkephalin modules; **weekly bonuses** multiply rewards and are limited per week.

Config switches that change the flow: `floor_3_exit` (leave after floor 3), `infinite_dungeons`, `save_rewards` (hard: do not claim), `re_formation_each_floor`, `auto_hard_mirror` (switch to hard on Thursday).

**Weekly bonus rule for agents**: bonuses belong to hard mirrors. Any normal mirror AALC runs for testing has `no_weekly_bonuses: 2` (see `docs/agents/device-testing.md`).

## Mirror vocabulary

- **E.G.O gift** (饰品, 饰品 = gift): passive item collected during a mirror. Has a **grade** I–IV (Roman numeral on the icon) and an **enhancement tier** `+` / `++` (orange crosses; `++` is max).
- **Keyword** (体系, also 本体系 = the team's chosen keyword, `self.system`): gift and team archetype. Code names ↔ Chinese:

  | code | 中文 | | code | 中文 |
  |---|---|---|---|---|
  | burn | 烧伤 | | poise | 呼吸 |
  | bleed | 流血 | | sinking | 沉沦 |
  | tremor | 震颤 | | charge | 充能 |
  | rupture | 破裂 | | slash / pierce / blunt | 斩击 / 突刺 / 打击 |

  Each gift shows its keyword as a small icon at the bottom right; AALC finds gifts by these icons (`mirror/shop/enhance_gifts/<keyword>.png`). A **second system** (`second_system`) is an optional secondary keyword.
- **Shop** (`in_shop.py: InShop.in_shop`), modules in order: ID skill replacement, heal sinners, **sell** gifts outside the keep list (`shop_sell_list`), **buy** keyword gifts and must-buy items, **refresh** / **keyword refresh** (re-roll goods, keyword refresh biases them to a keyword), **fuse** gifts (合成; towards grade IV), **power-up** (强化/升级) keyword gifts. Leave via Leave → confirm.
- **Fuse** (`fuse_gift`, `fuse_switch`, `fuse_aggressive_switch`): combine gifts into a higher grade; grade IV keyword gifts are a goal.
- **ID skill replacement** (技能替换): shop item that swaps a sinner's skill; AALC buys it for preferred sinners (OCR of the sinner name).
- **White cotton** (白棉花 / White Gossypium): a gift AALC avoids unless `not_skip_whitegossypium`.

## Battle vocabulary (`tasks/battle/battle.py`)

- **Sinners** (罪人): the 12 playable characters (YiSang, Faust, DonQuixote, Ryoshu, Meursault, HongLu, Heathcliff, Ishmael, Rodion, Sinclair, Outis, Gregor). An **Identity** is a sinner's variant with its own skills. A **team** is a saved formation picked before a mirror (`teams` config, team codes, `team_formation.py`).
- **Turn**: each sinner gets skill slots; the player assigns skills, then starts the turn. **P** = auto-assign by win rate, **Enter** = start (AALC's default "P+Enter"). The **pause** button is visible only while a turn plays.
- **Defense**: switching every slot to its defense skill, then linking (`_defense_this_round`). Used on turn 1 (`defense_on_turn1`), always (`defense_all_time`), or for a limited number of turns per mirror for **小指良单通** (`DefenseForSoloState`, log `小指良单通连续防御`; limit `DEFENSE_FOR_SOLO_TURN_LIMIT`).
- **小指良单通**: a play style that clears the normal mirror solo with one specific Ryoshu identity (小指良). AALC's support for it makes the team defend for the first turns of each mirror; a turn counts only if the turn actually started.
- **Chain / skill 3** (`_chain_battle`, `avoid_skill_3`, `prioritize_skill_3`): link slots by dragging to choose upper/lower (skill 3) rows.

## Code map

- Screen + input layer: `module/automation/automation.py` (`auto`), adapters in `module/automation/input_handlers/` (MuMu, other emulators, Win32). Pitfalls: `docs/agents/recognition-pitfalls.md`.
- Templates: `assets/images/default/{share,en,zh_cn}/...`; `*_assets.png` are full-screen 2560×1440 canvases whose non-black area is the search box.
- Config schema: `module/config/config_typing.py`; defaults only in `assets/config/config.example.yaml` (a test enforces the two match).
- Popups / disconnects: `tasks/base/retry.py` (`retry()` in almost every loop), `tasks/base/retry_monitor.py` (background).
- Back to the main menu from anywhere: `tasks/base/back_init_menu.py`.
