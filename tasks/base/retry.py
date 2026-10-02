import os
import platform
import time
from time import sleep

import psutil
import win32process

from module.automation import auto
from module.config import cfg
from module.game_and_screen import screen
from module.logger import log
from utils.utils import check_game_running

_last_title_screen_tap_time = 0.0
_last_simulator_alive_check_time = 0.0
# 业务循环几乎每轮都调用 retry()；上次完整检查后这么久内直接返回，省掉每轮的弹窗模板比对。
# 弹窗最多晚这么久才被处理（服务器重试弹窗另有 retry_monitor 每 0.5 秒检查）
RETRY_CHECK_INTERVAL = 1.0
_last_retry_check_time = 0.0


def ensure_simulator_game_started() -> bool:
    """模拟器模式下确认游戏仍在前台，不在时尝试拉起游戏。"""
    global _last_simulator_alive_check_time
    if not cfg.simulator:
        return False

    now = time.time()
    if now - _last_simulator_alive_check_time < 5:
        return False
    _last_simulator_alive_check_time = now

    if cfg.simulator_type == 0:
        from module.automation.input_handlers.simulator.mumu_control import (
            MumuControl,
        )

        connection_device = MumuControl.connection_device
    else:
        from module.automation.input_handlers.simulator.simulator_control import (
            SimulatorControl,
        )

        connection_device = SimulatorControl.connection_device

    if connection_device is None:
        return False

    if connection_device.check_game_alive():
        return False

    log.info("检测到游戏未运行或不在前台，尝试自动启动游戏")
    connection_device.start_game()
    sleep(3)
    return True


def click_title_screen_safely() -> None:
    """标题页点击入口，避开账号、清缓存和中间弹窗区域。"""
    global _last_title_screen_tap_time
    if not cfg.simulator:
        auto.mouse_click_blank()
        return

    now = time.time()
    if now - _last_title_screen_tap_time < 15:
        return
    _last_title_screen_tap_time = now

    height = int(cfg.set_win_size or 1080)
    width = int(height * 16 / 9)
    tap_points = ((0.86, 0.80), (0.74, 0.83), (0.91, 0.58))
    index = int(now // 10) % len(tap_points)
    x_ratio, y_ratio = tap_points[index]
    auto.mouse_click(int(width * x_ratio), int(height * y_ratio))


def kill_game():
    """关闭游戏"""
    if cfg.simulator:
        if cfg.simulator_type == 0:
            from module.automation.input_handlers.simulator.mumu_control import (
                MumuControl,
            )

            connection_device = MumuControl.connection_device
        else:
            from module.automation.input_handlers.simulator.simulator_control import (
                SimulatorControl,
            )

            connection_device = SimulatorControl.connection_device
        if connection_device is None:
            log.warning("模拟器连接当前不可用，跳过关闭游戏；后续初始化将重建连接")
            return
        connection_device.close_current_app()
        return
    if platform.system() == "Windows":
        from module.game_and_screen import screen

        _, pid = win32process.GetWindowThreadProcessId(screen.handle.hwnd)
        os.system(f"taskkill /F /PID {pid}")
    sleep(10)
    wait_start = time.time()
    while True:
        game_running = False
        for proc in psutil.process_iter(["name"]):
            try:
                # 获取进程的可执行文件名（如 "notepad.exe"）
                proc_name = proc.info["name"]
                # 仅当遍历后找不到任何游戏进程时，才认为游戏已退出
                if proc_name and cfg.game_process_name.lower() in proc_name.lower():
                    game_running = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # 忽略已终止、无权限或僵尸进程
                continue
        if not game_running:
            break
        if time.time() - wait_start > 30:
            log.warning("等待游戏进程退出超时(30s)，继续后续流程")
            break
        sleep(1)


def check_times(start_time, timeout=90, logs=True):
    """检查是否卡死超时，若是则尝试关闭重启游戏"""
    now_time = time.time()
    if logs and int(now_time - start_time) > 9 and int(now_time - start_time) % 10 == 0:
        log.info(f"初始时间为{time.strftime('%H:%M:%S', time.localtime(start_time))}，此刻时间为{time.strftime('%H:%M:%S', time.localtime(now_time))}，已卡死{int(now_time - start_time)}秒")
        sleep(1)
    if now_time - start_time > timeout:
        log.info(f"已卡死超过{timeout}秒，尝试关闭重启游戏")
        kill_game()
        restart_game()
        return True
    else:
        return False


def retry():
    """重试连接。

    首轮检查复用调用方刚截取、且之后没有发生输入的截图，避免再等一次 screenshot_interval；
    之后的循环（处理过弹窗或重启后）始终刷新截图，避免复用旧帧导致误判。
    距上次完整检查不足 RETRY_CHECK_INTERVAL 秒时直接返回。
    画面在持续操作下长时间不变（游戏卡死）时重启游戏并返回 False。
    """
    global _last_retry_check_time
    if auto.screen_frozen():
        log.warning(f"持续操作但画面超过 {auto.FROZEN_SCREEN_LIMIT} 秒没有变化，判定游戏卡死，尝试关闭重启游戏")
        auto.reset_frozen_watch()
        kill_game()
        restart_game()
        return False
    if time.time() - _last_retry_check_time < RETRY_CHECK_INTERVAL:
        # 跳过弹窗检查，但仍保证当前截图是新的：back_init_menu 等循环自己不截图，靠 retry() 刷新画面，
        # 否则会一直对着同一张旧图判断（重启游戏后 10 秒内就耗尽次数，陷入反复重启）
        if not auto.screenshot_is_fresh(cfg.screenshot_interval or 0.85):
            auto.take_screenshot()
        return None
    start_time = time.time()
    is_windows = not cfg.config.simulator
    if is_windows:
        saved_hwnd = screen.handle.hwnd
    reuse_screenshot = auto.screenshot_is_fresh(cfg.screenshot_interval or 0.85)
    while True:
        if ensure_simulator_game_started():
            start_time = time.time()
            reuse_screenshot = False
            continue
        if is_windows and screen.handle.hwnd != saved_hwnd:
            # 句柄发生变化则重置初始时间, 以免误判卡死
            saved_hwnd = screen.handle.hwnd
            start_time = time.time()
        if auto.get_restore_time() is not None:
            start_time = max(start_time, auto.get_restore_time())
        if check_times(start_time):
            return False
        if reuse_screenshot:
            reuse_screenshot = False
        elif auto.take_screenshot() is None:
            continue
        if auto.find_element("base/connecting_assets.png"):
            continue
        if position := auto.find_element("base/retry_countdown.png"):
            sleep(5)
            auto.mouse_click(position[0], position[1], times=3)
            continue
        if auto.click_element("base/retry.png", threshold=0.9):
            auto.mouse_to_blank()
            continue
        # retry_countdown 与阈值 0.9 的 retry 已在上面比对过，这里只补阈值 0.8 的 retry 和 try_again
        if auto.find_element("base/retry.png") or auto.find_element("base/try_again.png"):
            auto.click_element("base/retry.png", threshold=0.9)
            continue
        if auto.find_element("base/clear_all_caches_assets.png", model="clam"):
            if auto.click_element("base/update_confirm_assets.png"):
                continue
            click_title_screen_safely()
            continue
        if auto.click_element("base/only_option_assets.png", model="clam"):
            sleep(5)
            if not check_game_running():
                log.debug("检测到游戏未运行，调用 init_game() 重新初始化")
                from tasks.base.script_task_scheme import init_game

                init_game()
            continue
        _last_retry_check_time = time.time()
        break


def restart_game():
    """重启游戏"""
    from tasks.base.back_init_menu import back_init_menu
    from tasks.base.script_task_scheme import init_game

    init_game()
    sleep(3)
    back_init_menu()
