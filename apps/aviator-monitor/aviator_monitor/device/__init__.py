"""Camada de controle do device (BlueStacks Android 11) via ADB — o 'jeito do Hans'.

- `adb.Device`         : runner fino do ADB (shell/exec-out/screencap) sem mangling de path.
- `androui`            : lê a tela pela hierarquia de acessibilidade (uiautomator) → DataFrame.
- `cursor.Cursor`      : move o cursor de forma natural (motionevent MOVE) e clica (input tap).
- `bluestacks.BlueStacks`: sobe/derruba/consulta instâncias do BlueStacks sem cliques (conf + CLI).

Nada aqui usa root. Ver docs/08-controle-device-adb.md.
"""
from .adb import Device                       # noqa: F401
from .cursor import Cursor                     # noqa: F401
from .bluestacks import BlueStacks            # noqa: F401
