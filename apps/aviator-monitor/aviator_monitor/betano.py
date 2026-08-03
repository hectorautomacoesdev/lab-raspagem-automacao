"""Fluxo Betano: abrir o site/app → login → abrir o Aviator → deixar a tira visível p/ o coletor.

Princípios (linha ética do projeto):
  • Credenciais SÓ de variável de ambiente (BETANO_USER / BETANO_PASS). Nunca em arquivo/commit.
  • CAPTCHA: a gente DETECTA e AVISA (salva print + loga). NÃO resolve — se cair, para e chama o Hector.
  • Interação humana: usa o cursor natural (device/cursor) e lê a tela por DataFrame (device/androui),
    o "jeito do Hans". A robustez do glide é benefício de UI, não um toolkit de evasão de fraude.

Realidade honesta: os seletores exatos da Betano (resource-id/texto dos campos e botões) mudam e
só se acertam VENDO a tela real. Por isso este módulo tem `snapshot()` (print + DataFrame → CSV)
para calibrar, e os seletores default são heurísticos (casam por texto comum). Rode a calibração
uma vez, ajuste `Selectors`, e o login roda sozinho.

Uso típico (na máquina do Hector, com a instância no ar):
    set BETANO_USER=...&& set BETANO_PASS=...           (no PowerShell: $env:BETANO_USER=...)
    python -m aviator_monitor.betano snapshot            # calibra: salva print + screen.csv
    python -m aviator_monitor.betano login               # faz o login
    python -m aviator_monitor.betano aviator             # abre o Aviator
    python -m aviator_monitor.betano full                # site → login → aviator
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path

from .config import CONFIG, DATA_DIR
from .device import BlueStacks, Cursor, Device
from .device import androui

# Pistas de CAPTCHA/verificação anti-bot (varredura no DataFrame da tela). Só p/ DETECTAR.
CAPTCHA_MARKERS = [
    "captcha", "recaptcha", "hcaptcha", "cloudflare", "turnstile",
    "não sou um robô", "nao sou um robo", "not a robot", "i'm not a robot",
    "verificação", "verificacao", "verify you are human", "challenge",
    "prove you", "security check", "verifique",
]

# Pacotes comuns (ajuste conforme o que estiver instalado na instância).
CHROME_PKG = "com.android.chrome"
BETANO_URL = "https://www.betano.com"


def get_credentials() -> tuple[str, str]:
    """Lê BETANO_USER/BETANO_PASS do ambiente. Erro claro se faltarem (nunca hardcode)."""
    user = os.environ.get("BETANO_USER", "").strip()
    pw = os.environ.get("BETANO_PASS", "")
    if not user or not pw:
        raise RuntimeError(
            "Credenciais ausentes. Defina no ambiente (NÃO em arquivo):\n"
            '  PowerShell:  $env:BETANO_USER="seu_email"; $env:BETANO_PASS="sua_senha"\n'
            "As credenciais nunca são gravadas em disco por este projeto.")
    return user, pw


def escape_for_input_text(text: str) -> str:
    """Protege o texto p/ `input text '<...>'` no shell do device (aspas simples).

    Envolver em aspas simples torna literais os símbolos (ex.: '*', '$', '&') — sem glob/expansão.
    Aspas simples internas viram a sequência sh padrão '\\''. Espaços literais funcionam no
    Android 11 dentro das aspas (em ROMs antigas usa-se %s; as credenciais aqui não têm espaço).
    """
    return "'" + text.replace("'", "'\\''") + "'"


def detect_captcha(df) -> "list[str]":
    """Devolve as pistas de CAPTCHA encontradas no DataFrame da tela (vazio = nada detectado)."""
    if df is None or getattr(df, "empty", True):
        return []
    hay = (df["text"].fillna("").str.lower() + " "
           + df["desc"].fillna("").str.lower() + " "
           + df["resource_id"].fillna("").str.lower())
    found = set()
    for marker in CAPTCHA_MARKERS:
        if hay.str.contains(marker, regex=False, na=False).any():
            found.add(marker)
    return sorted(found)


@dataclass
class Selectors:
    """Heurísticas p/ achar campos/botões. Calibre com `snapshot` e ajuste aqui se preciso."""
    user_field: list[str] = field(default_factory=lambda: ["e-mail", "email", "usuário", "usuario", "login"])
    pass_field: list[str] = field(default_factory=lambda: ["senha", "password"])
    login_button: list[str] = field(default_factory=lambda: ["entrar", "login", "acessar"])
    aviator_search: list[str] = field(default_factory=lambda: ["aviator"])


class BetanoFlow:
    """Orquestra o fluxo no device já no ar. Não sobe a instância — use BlueStacks p/ isso."""

    def __init__(self, serial: str | None = None, instance: str = "Rvc64",
                 chrome_pkg: str = CHROME_PKG, url: str = BETANO_URL,
                 selectors: Selectors | None = None):
        self.bs = BlueStacks()
        self.serial = serial or self.bs.adb_serial(instance) or CONFIG.device_serial
        self.dev = Device(serial=self.serial)
        self.cursor = Cursor(self.dev)
        self.chrome_pkg = chrome_pkg
        self.url = url
        self.sel = selectors or Selectors()
        self.shots = DATA_DIR / "shots"
        self.shots.mkdir(exist_ok=True)

    # -- infra --
    def ensure_online(self) -> None:
        self.dev.connect()
        if not self.dev.is_online():
            raise RuntimeError(
                f"device {self.serial} offline. Suba a instância e ligue o ADB:\n"
                "  python -m aviator_monitor.device.bluestacks start Rvc64\n"
                "  python -m aviator_monitor.device.bluestacks wait  Rvc64")

    def _screen(self):
        return androui.screen_df(self.dev)

    def _save_shot(self, name: str) -> Path:
        frame = self.dev.screencap()
        path = self.shots / f"{name}-{time.strftime('%Y%m%d-%H%M%S')}.png"
        if frame is not None:
            import cv2
            cv2.imwrite(str(path), frame)
        return path

    def _tap_by_text(self, needles: list[str], df=None) -> bool:
        """Acha o 1º nó cujo texto/desc casa (case-insensitive) e clica com glide humano."""
        df = df if df is not None else self._screen()
        for needle in needles:
            hit = androui.find(df, contains=needle)
            if not hit.empty:
                r = hit.iloc[0]
                self.cursor.move_and_click(int(r["cx"]), int(r["cy"]))
                return True
        return False

    def _type(self, text: str) -> None:
        self.dev.sh(f"input text {escape_for_input_text(text)}")

    def _guard_captcha(self, stage: str) -> list[str]:
        """Se houver CAPTCHA, salva print e devolve as pistas (chamador decide parar)."""
        found = detect_captcha(self._screen())
        if found:
            shot = self._save_shot(f"captcha-{stage}")
            print(f"  ⚠️  CAPTCHA detectado em '{stage}': {found}")
            print(f"      Print salvo: {shot}")
            print("      (Este projeto NÃO resolve CAPTCHA — resolva manualmente e siga.)")
        return found

    # -- passos --
    def open_site(self) -> None:
        """Abre a URL no Chrome via intent VIEW (limpo e confiável)."""
        self.ensure_online()
        self.dev.sh(
            f"am start -a android.intent.action.VIEW -d {self.url} {self.chrome_pkg}")
        time.sleep(5)

    def snapshot(self, tag: str = "screen") -> tuple[Path, Path]:
        """Calibração: salva print + DataFrame da tela em CSV para você ajustar os Selectors."""
        self.ensure_online()
        df = self._screen()
        shot = self._save_shot(tag)
        csv = self.shots / f"{tag}-{time.strftime('%Y%m%d-%H%M%S')}.csv"
        df.to_csv(csv, index=False, encoding="utf-8-sig")
        print(f"  Print : {shot}")
        print(f"  Tela  : {csv}  ({len(df)} nós)")
        cap = detect_captcha(df)
        print(f"  CAPTCHA: {cap or 'nenhum sinal'}")
        return shot, csv

    def login(self) -> bool:
        """Preenche usuário/senha (de ENV) e envia. Para se detectar CAPTCHA."""
        user, pw = get_credentials()
        self.ensure_online()
        if self._guard_captcha("pre-login"):
            return False
        df = self._screen()
        if not self._tap_by_text(self.sel.user_field, df):
            print("  ✗ campo de usuário não achado — rode `snapshot` e ajuste Selectors.user_field")
            return False
        self._type(user)
        time.sleep(0.6)
        if not self._tap_by_text(self.sel.pass_field):
            print("  ✗ campo de senha não achado — ajuste Selectors.pass_field")
            return False
        self._type(pw)
        time.sleep(0.6)
        if self._guard_captcha("antes-de-enviar"):
            return False
        if not self._tap_by_text(self.sel.login_button):
            print("  ✗ botão de login não achado — ajuste Selectors.login_button")
            return False
        time.sleep(5)
        if self._guard_captcha("pos-login"):
            return False
        print("  ✓ login enviado (confira o resultado na tela).")
        return True

    def open_aviator(self) -> bool:
        """Procura e abre o Aviator. Deixa a tira de histórico visível p/ o run.py."""
        self.ensure_online()
        df = self._screen()
        if self._tap_by_text(self.sel.aviator_search, df):
            time.sleep(4)
            print("  ✓ Aviator aberto (calibre CONFIG.strip_roi com um print da tira).")
            self._save_shot("aviator")
            return True
        print("  ✗ Aviator não achado na tela — navegue até o cassino e rode de novo, "
              "ou use a busca do site.")
        return False

    def full(self) -> None:
        self.open_site()
        self.login()
        self.open_aviator()


def main():
    import argparse
    ap = argparse.ArgumentParser(
        prog="python -m aviator_monitor.betano",
        description="Fluxo Betano (site→login→aviator). Credenciais só de ENV.")
    ap.add_argument("cmd", choices=["snapshot", "site", "login", "aviator", "full"])
    ap.add_argument("--instance", default="Rvc64")
    ap.add_argument("--serial", default=None)
    args = ap.parse_args()

    flow = BetanoFlow(serial=args.serial, instance=args.instance)
    if args.cmd == "snapshot":
        flow.snapshot()
    elif args.cmd == "site":
        flow.open_site()
    elif args.cmd == "login":
        flow.login()
    elif args.cmd == "aviator":
        flow.open_aviator()
    elif args.cmd == "full":
        flow.full()


if __name__ == "__main__":
    main()
