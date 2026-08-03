"""Exemplo: controlar o device do 'jeito do Hans' — ler a tela (uiautomator → DataFrame)
e agir com o cursor (movimento natural + clique), SEM screenshot/OCR para a navegação.

Fluxo: HOME → abre a pasta 'Aplicativos do sistema' → abre o Chrome → dentro do Chrome
acha um botão POR TEXTO e clica. A cada passo, imprime a hierarquia como DataFrame.

Rodar (a partir de apps/aviator-monitor, com o venv do projeto e o BlueStacks Android 11 no ar):
    $py = "..\..\.venv-scraping\Scripts\python.exe"
    & $py examples\demo_cursor_uiautomator.py
"""
from __future__ import annotations

import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # console Windows fala cp1252
except Exception:
    pass

import pandas as pd

from aviator_monitor.device import Cursor, Device, androui

pd.set_option("display.width", 160)


def show(df: pd.DataFrame) -> None:
    """Mostra só os nós úteis (clicáveis ou com texto)."""
    cols = ["text", "resource_id", "clickable", "cx", "cy", "w", "h"]
    view = df[df["clickable"] | (df["text"] != "")][cols]
    print(view.to_string(index=False, max_colwidth=32))


def main() -> None:
    dev = Device()                      # 127.0.0.1:5555 (Android 11 / Rvc64)
    cur = Cursor(dev, start=(10, 10))
    print("connect:", dev.connect(), "| online:", dev.is_online(),
          "| tela:", dev.screen_size())

    dev.back(); dev.back(); dev.home(); time.sleep(1.0)          # estado limpo

    # 1) HOME — ler a tela e localizar a pasta pela hierarquia (não por coordenada fixa)
    home = androui.screen_df(dev)
    print("\n[1] HOME:"); show(home)
    top = home[home["clickable"] & home["cy"].between(150, 300) & (home["w"] > 150)]
    top = top.sort_values("cx")
    folder = (int(top.iloc[1]["cx"]), int(top.iloc[1]["cy"]))    # 2ª célula = a pasta

    # 2) cursor desliza até a pasta e clica
    print(f"\n[2] cursor → pasta {folder}")
    cur.move_and_click(*folder, seed=1); time.sleep(1.2)

    # 3) pasta aberta: Chrome é a 3ª célula de app (sem texto no launcher do BlueStacks)
    folder_df = androui.screen_df(dev)
    cells = folder_df[folder_df["clickable"] & (folder_df["text"] == "")
                      & folder_df["cy"].between(240, 390) & folder_df["w"].between(50, 120)]
    cells = cells.sort_values("cx")
    chrome = (int(cells.iloc[2]["cx"]), int(cells.iloc[2]["cy"]))
    print(f"\n[3] pasta aberta — Chrome (3ª célula) = {chrome}")

    # 4) cursor desliza até o Chrome e clica
    cur.move_and_click(*chrome, seed=2); time.sleep(3.0)
    print("    foco:", androui.focus_info(dev).splitlines()[0])

    # 5) dentro do Chrome a hierarquia vem ROTULADA → acha o botão por TEXTO
    chrome_df = androui.screen_df(dev)
    print("\n[5] CHROME (hierarquia rotulada):"); show(chrome_df)
    for kw in ("without", "sem uma conta", "no thanks", "usar"):
        c = androui.center_of(chrome_df, contains=kw)
        if c:
            print(f"    achei '{kw}' em {c} → cursor + clique")
            cur.move_and_click(*c, seed=3)
            break

    print("\nOK")


if __name__ == "__main__":
    main()
