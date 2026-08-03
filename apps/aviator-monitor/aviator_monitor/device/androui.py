"""Ler a tela pela HIERARQUIA DE ACESSIBILIDADE — o 'jeito do Hans': tela → DataFrame.

Sem screenshot e sem OCR: `uiautomator dump` devolve um XML com todos os nós visíveis
(text, content-desc, resource-id, class, bounds, clickable…). Nós viramos isso num
`pandas.DataFrame` — exatamente o padrão "DOM inteiro → DataFrame" que o Hans aplica no
scraping web (e no Android via o repo dele `androdf`). Com o DataFrame, achar um elemento
é um `.query()`/filtro, e clicar é ir ao centro (`cx, cy`) dele.

Dois jeitos de "saber o que há na tela" (ambos sem OCR):
  1. `screen_df()`  — hierarquia completa (uiautomator). Rico: todo nó clicável e seu texto.
  2. `focus_info()` — atividade/janela em foco (dumpsys). Barato: saber ONDE estamos.

Limitação honesta (medida no device): o launcher do BlueStacks (com.uncube.launcher3)
NÃO rotula os ícones dentro de pastas (text=""), então lá o DataFrame dá só a estrutura
(as células e seus bounds). Dentro de apps reais (Chrome, casa de aposta) a hierarquia
vem rotulada e o `find(text=...)` funciona pleno.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET

import pandas as pd

from .adb import Device

_BOUNDS_RE = re.compile(r"\[(-?\d+),(-?\d+)\]\[(-?\d+),(-?\d+)\]")

COLUMNS = ["text", "desc", "resource_id", "class", "package",
           "clickable", "enabled", "x1", "y1", "x2", "y2",
           "cx", "cy", "w", "h", "area"]


def _parse_bounds(s: str | None):
    m = _BOUNDS_RE.match(s or "")
    if not m:
        return 0, 0, 0, 0
    return tuple(int(v) for v in m.groups())


def dump_xml(dev: Device, remote: str = "/sdcard/uidump.xml") -> str:
    """Gera o dump no device e traz o XML como texto (via exec-out cat)."""
    dev.sh(f"uiautomator dump {remote}")
    return dev.exec_out(f"cat {remote}").decode("utf-8", "replace")


def parse(xml_text: str) -> pd.DataFrame:
    """XML do uiautomator → DataFrame com um nó por linha (offline-testável)."""
    rows = []
    if xml_text.strip():
        root = ET.fromstring(xml_text)
        for n in root.iter("node"):
            a = n.attrib
            x1, y1, x2, y2 = _parse_bounds(a.get("bounds"))
            rows.append({
                "text": a.get("text", ""),
                "desc": a.get("content-desc", ""),
                "resource_id": a.get("resource-id", ""),
                "class": a.get("class", ""),
                "package": a.get("package", ""),
                "clickable": a.get("clickable") == "true",
                "enabled": a.get("enabled") == "true",
                "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                "cx": (x1 + x2) // 2, "cy": (y1 + y2) // 2,
                "w": x2 - x1, "h": y2 - y1, "area": (x2 - x1) * (y2 - y1),
            })
    return pd.DataFrame(rows, columns=COLUMNS)


def screen_df(dev: Device) -> pd.DataFrame:
    """Lê a tela agora e devolve o DataFrame da hierarquia."""
    return parse(dump_xml(dev))


def find(df: pd.DataFrame, text=None, desc=None, contains=None,
         resource_id=None, clickable=None) -> pd.DataFrame:
    """Filtra nós. `contains` casa em text OU desc (case-insensitive)."""
    m = pd.Series(True, index=df.index)
    if text is not None:
        m &= df["text"] == text
    if desc is not None:
        m &= df["desc"] == desc
    if contains is not None:
        c = contains.lower()
        m &= (df["text"].str.lower().str.contains(c, na=False)
              | df["desc"].str.lower().str.contains(c, na=False))
    if resource_id is not None:
        m &= df["resource_id"] == resource_id
    if clickable is not None:
        m &= df["clickable"] == clickable
    return df[m]


def center_of(df: pd.DataFrame, **kw) -> tuple[int, int] | None:
    """Centro (cx, cy) do 1º nó que casa com o filtro, ou None."""
    hit = find(df, **kw)
    if hit.empty:
        return None
    r = hit.iloc[0]
    return int(r["cx"]), int(r["cy"])


def focus_info(dev: Device) -> str:
    """2º jeito de saber a tela: atividade/janela em foco (barato, via dumpsys)."""
    return dev.sh("dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'").strip()
