"""Testes offline da camada de device (sem ADB): parsing do uiautomator + geometria do cursor.
Rode: python tests/test_device.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aviator_monitor.device import androui
from aviator_monitor.device.cursor import human_path

_XML = """<?xml version='1.0' encoding='UTF-8'?>
<hierarchy rotation="0">
  <node text="" resource-id="root" class="android.widget.FrameLayout" bounds="[0,0][1280,720]">
    <node text="Chrome" content-desc="" resource-id="" class="android.widget.TextView"
          clickable="true" enabled="true" package="com.android.chrome" bounds="[566,246][640,374]"/>
    <node text="Usar sem uma conta" resource-id="btn" class="android.widget.Button"
          clickable="true" enabled="true" package="com.android.chrome" bounds="[456,346][1208,392]"/>
  </node>
</hierarchy>"""


def test_parse_bounds():
    assert androui._parse_bounds("[566,246][640,374]") == (566, 246, 640, 374)
    assert androui._parse_bounds(None) == (0, 0, 0, 0)
    assert androui._parse_bounds("lixo") == (0, 0, 0, 0)


def test_parse_to_dataframe():
    df = androui.parse(_XML)
    assert len(df) == 3                                   # 3 nós
    chrome = androui.find(df, text="Chrome").iloc[0]
    assert (int(chrome["cx"]), int(chrome["cy"])) == (603, 310)   # centro da célula do Chrome
    assert chrome["clickable"] is True or chrome["clickable"] == True
    # busca por substring casa em text (case-insensitive)
    assert androui.center_of(df, contains="sem uma conta") == (832, 369)
    assert androui.center_of(df, text="Inexistente") is None
    # colunas estáveis mesmo com XML vazio
    assert list(androui.parse("").columns) == androui.COLUMNS


def test_human_path_geometry():
    pts = human_path((10, 10), (600, 300), steps=20, seed=7)
    assert len(pts) == 20
    assert pts[-1] == (600, 300)                          # termina EXATO no alvo
    # todos os pontos são inteiros e ficam dentro de uma caixa razoável do trajeto
    assert all(isinstance(x, int) and isinstance(y, int) for x, y in pts)
    xs = [x for x, _ in pts]
    assert min(xs) >= -20 and max(xs) <= 620
    # determinístico com a mesma seed
    assert human_path((10, 10), (600, 300), steps=20, seed=7) == pts


if __name__ == "__main__":
    test_parse_bounds()
    test_parse_to_dataframe()
    test_human_path_geometry()
    print("OK - testes de device passaram")
