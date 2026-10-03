"""LDPlayer 9 (>= 9.0.78) 的 ldopengl64.dll 截图：直接读模拟器渲染缓冲，比 adb screencap 快得多。

接口（MaaFramework / ALAS 同样用法）：
    CreateScreenShotInstance(index, player_pid) -> IScreenShotClass*
    IScreenShotClass 虚表：[1] cap() -> 宽*高*3 的 BGR 缓冲（上下颠倒），[2] release()
player_pid 与分辨率取自 `ldconsole.exe list2`。
"""

import ctypes
import os
import subprocess

import numpy as np
import psutil

from module.logger import log

LD_ADB_BASE_PORT = 5555


class LDOpenGL:
    def __init__(self, ld_folder: str, index: int):
        self.lib = ctypes.WinDLL(os.path.join(ld_folder, "ldopengl64.dll"))
        out = subprocess.run(
            [os.path.join(ld_folder, "ldconsole.exe"), "list2"], capture_output=True, timeout=10
        ).stdout
        row = next(
            (r.split(b",") for r in out.splitlines() if r.split(b",")[0].strip() == str(index).encode()), None
        )
        if row is None or len(row) != 10 or row[4].strip() != b"1":
            raise RuntimeError(f"LDPlayer 实例 {index} 未运行: {row}")
        player_pid, self.width, self.height = int(row[5]), int(row[7]), int(row[8])

        self.lib.CreateScreenShotInstance.restype = ctypes.c_void_p
        self._instance = ctypes.c_void_p(self.lib.CreateScreenShotInstance(index, player_pid))
        if not self._instance.value:
            raise RuntimeError("CreateScreenShotInstance 返回空指针")
        # 虚表第 1、2 项：cap、release（this 指针作为第一个参数）
        self._cap = ctypes.WINFUNCTYPE(ctypes.c_void_p)(1, "cap")
        self._release = ctypes.WINFUNCTYPE(None)(2, "release")

    def screenshot(self) -> np.ndarray:
        """BGR 数组，与 adb 截图（cv2.imdecode）一致。"""
        ptr = self._cap(self._instance)
        if not ptr:
            raise RuntimeError("ldopengl 截图返回空指针")
        size = self.height * self.width * 3
        buf = ctypes.cast(ptr, ctypes.POINTER(ctypes.c_ubyte * size)).contents
        # 缓冲按 y 轴向上存放，上下翻转（同时复制出缓冲）
        return np.ctypeslib.as_array(buf).reshape(self.height, self.width, 3)[::-1].copy()

    def __del__(self):
        if getattr(self, "_instance", None) and self._instance.value:
            self._release(self._instance)


def try_ldopengl(port: int) -> LDOpenGL | None:
    """端口落在 LDPlayer 的 5555 + 2*index 范围、且找到正在运行的 dnplayer.exe 时启用；否则返回 None 走 adb。"""
    if not (LD_ADB_BASE_PORT <= port <= LD_ADB_BASE_PORT + 64 and (port - LD_ADB_BASE_PORT) % 2 == 0):
        return None
    folder = next(
        (os.path.dirname(p.info["exe"]) for p in psutil.process_iter(["name", "exe"])
         if (p.info["name"] or "").lower() == "dnplayer.exe" and p.info["exe"]),
        None,
    )
    if folder is None or not os.path.exists(os.path.join(folder, "ldopengl64.dll")):
        return None
    try:
        capture = LDOpenGL(folder, (port - LD_ADB_BASE_PORT) // 2)
        capture.screenshot()
    except Exception as e:
        log.debug(f"ldopengl 截图不可用，改用 adb：{e}")
        return None
    log.debug(f"使用 ldopengl 截图：{folder}，{capture.width}x{capture.height}")
    return capture
