"""Runner fino do ADB para controlar o BlueStacks (Android 11, instância Rvc64).

Ponto sutil de Windows/Git-Bash: se um argumento do `adb shell` começa com `/`, o
MSYS reescreve o caminho (`/sdcard/ui.xml` virou `/Files/Git/sdcard/ui.xml` nos testes).
Por isso mandamos cada comando remoto como UMA string única (não começa com `/`), o que
desliga a conversão. Screenshots vêm por `exec-out` (binário puro, sem TTY).
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

DEFAULT_SERIAL = "127.0.0.1:5555"           # BlueStacks Android 11 (Rvc64), ADB ligado


def _find_adb() -> str:
    """adb.exe: env ADB_EXE > tools/platform-tools do repo > 'adb' do PATH."""
    env = os.environ.get("ADB_EXE")
    if env and Path(env).exists():
        return env
    exe = "adb.exe" if os.name == "nt" else "adb"
    for parent in Path(__file__).resolve().parents:
        cand = parent / "tools" / "platform-tools" / exe
        if cand.exists():
            return str(cand)
    return "adb"


ADB = _find_adb()


class Device:
    """Wrapper de um device ADB. Todos os comandos remotos vão como string única."""

    def __init__(self, serial: str = DEFAULT_SERIAL, adb: str = ADB):
        self.serial = serial
        self.adb = adb

    # -- infra --
    def _base(self) -> list[str]:
        return [self.adb, "-s", self.serial]

    def connect(self) -> str:
        r = subprocess.run([self.adb, "connect", self.serial],
                           capture_output=True, text=True)
        return r.stdout.strip()

    def sh(self, command: str, timeout: float = 20.0) -> str:
        """`adb -s SERIAL shell '<command>'` → stdout (texto)."""
        r = subprocess.run(self._base() + ["shell", command],
                           capture_output=True, text=True, timeout=timeout)
        return r.stdout

    def exec_out(self, command: str, timeout: float = 20.0) -> bytes:
        """`adb -s SERIAL exec-out '<command>'` → stdout (bytes, sem conversão de EOL)."""
        r = subprocess.run(self._base() + ["exec-out", command],
                           capture_output=True, timeout=timeout)
        return r.stdout

    # -- introspecção --
    def is_online(self) -> bool:
        return self.sh("getprop sys.boot_completed").strip() == "1"

    def screen_size(self) -> tuple[int, int]:
        """(largura, altura) via `wm size` → 'Physical size: 1280x720'."""
        import re
        m = re.search(r"(\d+)\s*x\s*(\d+)", self.sh("wm size"))
        return (int(m.group(1)), int(m.group(2))) if m else (0, 0)

    def current_focus(self) -> str:
        return self.sh("dumpsys window | grep -E 'mCurrentFocus'").strip()

    # -- captura --
    def screencap(self):
        """Frame atual como np.ndarray BGR (uint8) ou None. Requer opencv+numpy."""
        import cv2
        import numpy as np
        raw = self.exec_out("screencap -p")
        if not raw:
            return None
        return cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)

    # -- teclas úteis --
    def key(self, keycode: str) -> None:
        self.sh(f"input keyevent {keycode}")

    def home(self) -> None:
        self.key("KEYCODE_HOME")

    def back(self) -> None:
        self.key("KEYCODE_BACK")
