"""Controle do BlueStacks pela linha de comando + `bluestacks.conf` — o ambiente sobe/desce sem cliques.

Motivação: toda sessão o Hector precisava abrir o Multi-Instance Manager na mão, criar/ligar a
instância e ligar o toggle do ADB. O BlueStacks 5 não tem um CLI oficial completo, mas expõe
TRÊS superfícies que dão pra automatizar tudo isso:

  1. `HD-Player.exe --instance <nome> [--cmd launchApp --package <pkg>]`  → sobe a instância / abre um app
  2. `bluestacks.conf` (texto ~ini) → toda setting por instância: adb_port, ram, dpi, enable_adb_access…
  3. Registro `HKLM\\SOFTWARE\\BlueStacks_nxt` → DataDir, InstallDir, Version

Porta ADB: cada instância tem `bst.instance.<nome>.status.adb_port` (viva) e `.adb_port` (configurada).
Lemos da conf em vez de chutar 5555 (o gotcha que já pegou a gente). Se `bstconnect` (do Hans)
estiver instalado, dá pra descobrir portas dinâmicas via DataFrame — usamos como reforço opcional.

O parsing/edição da conf é feito por FUNÇÕES PURAS (`parse_conf`, `set_conf_line`) para ser
testável offline sem tocar no arquivo real. Toda escrita no arquivo faz BACKUP antes.
"""
from __future__ import annotations

import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

# Caminhos padrão desta máquina (validados); o registro é a fonte de verdade quando disponível.
_DEFAULT_INSTALL = Path(r"C:\Program Files\BlueStacks_nxt")
_DEFAULT_DATA = Path(r"C:\ProgramData\BlueStacks_nxt")


# --------------------------------------------------------------------------- #
# Funções puras de conf (testáveis offline)
# --------------------------------------------------------------------------- #
def parse_conf(text: str) -> dict[str, str]:
    """`bluestacks.conf` → dict {chave: valor} (aspas removidas). Ignora comentários/linhas vazias."""
    out: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        out[key.strip()] = val.strip().strip('"')
    return out


def set_conf_line(text: str, key: str, value: str) -> str:
    """Devolve o texto da conf com `key="value"` (substitui a linha existente ou anexa).

    Edição por linha (não regrava a partir do dict) para PRESERVAR ordem e comentários.
    """
    new_line = f'{key}="{value}"'
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith(key + "="):
            lines[i] = new_line
            break
    else:
        lines.append(new_line)
    # preserva a quebra de linha final se havia
    trailing = "\n" if text.endswith("\n") else ""
    return "\n".join(lines) + trailing


def instance_names_from_conf(conf: dict[str, str]) -> list[str]:
    """Instâncias declaradas em `bst.installed_images="A,B,..."`."""
    raw = conf.get("bst.installed_images", "")
    return [s for s in (p.strip() for p in raw.split(",")) if s]


# --------------------------------------------------------------------------- #
# Controlador
# --------------------------------------------------------------------------- #
class BlueStacks:
    """Sobe/derruba/consulta instâncias do BlueStacks sem cliques.

    Operações CONFIÁVEIS (uso diário): list, ports, start, stop, set_adb, wait_ready, launch_app.
    Operação EXPERIMENTAL (arriscada, faz backup e exige confirmação): clone_instance.
    """

    def __init__(self, install_dir: Path | None = None, conf_path: Path | None = None):
        self.install_dir = Path(install_dir) if install_dir else self._detect_install_dir()
        self.conf_path = Path(conf_path) if conf_path else self._detect_conf_path()
        self.player = self.install_dir / "HD-Player.exe"

    # -- descoberta de caminhos --
    @staticmethod
    def _registry() -> dict[str, str]:
        """Lê HKLM\\SOFTWARE\\BlueStacks_nxt (InstallDir, UserDefinedDir, DataDir, Version)."""
        try:
            import winreg
        except ImportError:  # não-Windows
            return {}
        for hive_path in (r"SOFTWARE\BlueStacks_nxt", r"SOFTWARE\WOW6432Node\BlueStacks_nxt"):
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, hive_path) as k:
                    out = {}
                    for name in ("InstallDir", "UserDefinedDir", "DataDir", "Version"):
                        try:
                            out[name] = winreg.QueryValueEx(k, name)[0]
                        except FileNotFoundError:
                            pass
                    if out:
                        return out
            except OSError:
                continue
        return {}

    def _detect_install_dir(self) -> Path:
        reg = self._registry().get("InstallDir")
        p = Path(reg) if reg else _DEFAULT_INSTALL
        return p if p.exists() else _DEFAULT_INSTALL

    def _detect_conf_path(self) -> Path:
        reg = self._registry().get("UserDefinedDir")
        base = Path(reg) if reg else _DEFAULT_DATA
        cand = base / "bluestacks.conf"
        return cand if cand.exists() else _DEFAULT_DATA / "bluestacks.conf"

    # -- conf: leitura/escrita com backup --
    def read_conf(self) -> dict[str, str]:
        return parse_conf(self.conf_path.read_text(encoding="utf-8", errors="replace"))

    def _backup_conf(self) -> Path:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        bak = self.conf_path.with_suffix(f".conf.bak-{stamp}")
        shutil.copy2(self.conf_path, bak)
        return bak

    def set_key(self, key: str, value: str) -> Path:
        """Grava `key="value"` na conf (com backup). Devolve o caminho do backup.

        Atenção: o BlueStacks reescreve a conf ao FECHAR o player. Edite com o player
        da instância PARADO, senão a alteração pode ser sobrescrita.
        """
        bak = self._backup_conf()
        text = self.conf_path.read_text(encoding="utf-8", errors="replace")
        self.conf_path.write_text(set_conf_line(text, key, value), encoding="utf-8")
        return bak

    # -- instâncias --
    def list_instances(self) -> list[str]:
        """Instâncias registradas (união da conf com as pastas em Engine/)."""
        conf = self.read_conf()
        names = set(instance_names_from_conf(conf))
        engine = self.install_dir  # fallback; a Engine real vem do DataDir
        data_dir = Path(self._registry().get("DataDir", str(_DEFAULT_DATA / "Engine")))
        for base in (data_dir, engine):
            if base.exists():
                for d in base.iterdir():
                    if d.is_dir() and d.name not in ("Manager", "UserData"):
                        # só considera pasta que aparece na conf p/ evitar lixo
                        if f"bst.instance.{d.name}.adb_port" in conf:
                            names.add(d.name)
        return sorted(names)

    def instance_prop(self, instance: str, prop: str, default: str = "") -> str:
        return self.read_conf().get(f"bst.instance.{instance}.{prop}", default)

    def adb_port(self, instance: str) -> int | None:
        """Porta ADB da instância: prioriza a viva (`status.adb_port`), cai p/ a configurada."""
        conf = self.read_conf()
        for key in (f"bst.instance.{instance}.status.adb_port",
                    f"bst.instance.{instance}.adb_port"):
            v = conf.get(key, "").strip()
            if v.isdigit():
                return int(v)
        return None

    def adb_serial(self, instance: str) -> str | None:
        port = self.adb_port(instance)
        return f"127.0.0.1:{port}" if port else None

    def ports(self) -> dict[str, int | None]:
        """{instância: porta_adb} — usa bstconnect (Hans) se instalado; senão lê a conf."""
        try:
            import bstconnect
            from .adb import ADB
            df = bstconnect.connect_to_all_localhost_devices(
                adb_path=ADB, timeout=3, bluestacks_config=str(self.conf_path))
            if hasattr(df, "empty") and not df.empty and "bst_instance" in df.columns:
                out = {}
                for _, row in df.iterrows():
                    host = str(row.get("localhost", ""))
                    port = int(host.rsplit(":", 1)[-1]) if ":" in host else None
                    out[str(row["bst_instance"])] = port
                if out:
                    return out
        except Exception:
            pass  # fallback silencioso p/ a conf
        return {name: self.adb_port(name) for name in self.list_instances()}

    # -- processos (via PowerShell CIM: pega a cmdline por instância) --
    def _player_procs(self) -> list[tuple[int, str]]:
        """(pid, cmdline) de cada HD-Player.exe rodando."""
        ps = ("Get-CimInstance Win32_Process -Filter \"Name='HD-Player.exe'\" | "
              "ForEach-Object { \"$($_.ProcessId)`t$($_.CommandLine)\" }")
        try:
            r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                               capture_output=True, text=True, timeout=15)
        except (OSError, subprocess.TimeoutExpired):
            return []
        out = []
        for line in r.stdout.splitlines():
            pid, _, cmd = line.partition("\t")
            if pid.strip().isdigit():
                out.append((int(pid), cmd))
        return out

    def is_running(self, instance: str) -> bool:
        needle = f"--instance {instance}".lower()
        return any(needle in cmd.lower() for _, cmd in self._player_procs())

    def _pid_of(self, instance: str) -> int | None:
        needle = f"--instance {instance}".lower()
        for pid, cmd in self._player_procs():
            if needle in cmd.lower():
                return pid
        return None

    # -- ADB global --
    def adb_enabled(self) -> bool:
        return self.read_conf().get("bst.enable_adb_access", "0") == "1"

    def set_adb(self, enabled: bool = True) -> Path:
        """Liga/desliga o ADB (setting global `bst.enable_adb_access`). Requer player parado."""
        return self.set_key("bst.enable_adb_access", "1" if enabled else "0")

    # -- ciclo de vida --
    def start(self, instance: str, package: str | None = None) -> subprocess.Popen:
        """Sobe a instância (e opcionalmente já abre um app). Não bloqueia — use wait_ready."""
        if not self.player.exists():
            raise FileNotFoundError(f"HD-Player não encontrado: {self.player}")
        cmd = [str(self.player), "--instance", instance]
        if package:
            cmd += ["--cmd", "launchApp", "--package", package]
        return subprocess.Popen(cmd)

    def launch_app(self, instance: str, package: str) -> subprocess.Popen:
        """Abre um app numa instância (sobe a instância se preciso). Ex.: 'com.android.chrome'."""
        return self.start(instance, package=package)

    def stop(self, instance: str) -> bool:
        """Fecha SÓ a instância indicada (taskkill do HD-Player com aquele --instance)."""
        pid = self._pid_of(instance)
        if pid is None:
            return False
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                       capture_output=True, text=True)
        return True

    def wait_ready(self, instance: str, timeout: float = 120.0) -> str:
        """Espera o Android terminar de bootar e devolve o serial ADB pronto p/ conectar.

        Resolve a porta da conf, conecta o ADB e faz poll de `sys.boot_completed`.
        """
        from .adb import Device
        deadline = time.time() + timeout
        serial = None
        while time.time() < deadline:
            serial = self.adb_serial(instance)
            if serial:
                dev = Device(serial=serial)
                dev.connect()
                try:
                    if dev.is_online():
                        return serial
                except subprocess.TimeoutExpired:
                    pass
            time.sleep(3)
        raise TimeoutError(
            f"instância '{instance}' não ficou pronta em {timeout:.0f}s "
            f"(serial={serial}). Confira se o ADB está ligado (set_adb) e a instância subiu.")

    def status(self, instance: str) -> dict:
        """Resumo de uma instância para diagnóstico rápido."""
        return {
            "instance": instance,
            "running": self.is_running(instance),
            "adb_enabled": self.adb_enabled(),
            "adb_serial": self.adb_serial(instance),
            "display_name": self.instance_prop(instance, "display_name"),
            "abi_list": self.instance_prop(instance, "abi_list"),
            "ram_mb": self.instance_prop(instance, "ram"),
            "resolution": f"{self.instance_prop(instance, 'fb_width')}x"
                          f"{self.instance_prop(instance, 'fb_height')}",
            "dpi": self.instance_prop(instance, "dpi"),
            "root": self.instance_prop(instance, "enable_root_access") == "1",
        }

    # -- EXPERIMENTAL: clonar instância --------------------------------------- #
    def clone_instance(self, source: str, dest: str, confirm: bool = False) -> str:
        """Clona `source`→`dest` copiando a pasta Engine + duplicando as chaves da conf.

        ⚠️ EXPERIMENTAL e ARRISCADO: copia vários GB e mexe na conf que sustenta a instância
        que já funciona. Faz backup da conf e exige confirm=True. Para o PRIMEIRO clone, o
        Multi-Instance Manager (GUI) ainda é o caminho mais seguro. Aqui fica para automação
        de escala depois de validado.
        """
        if not confirm:
            raise RuntimeError("clone_instance é experimental: passe confirm=True para prosseguir.")
        conf = self.read_conf()
        if dest in instance_names_from_conf(conf):
            raise ValueError(f"instância '{dest}' já existe na conf.")
        if self.is_running(source):
            raise RuntimeError(f"pare a instância '{source}' antes de clonar.")

        data_dir = Path(self._registry().get("DataDir", str(_DEFAULT_DATA / "Engine")))
        src_dir, dst_dir = data_dir / source, data_dir / dest
        if not src_dir.exists():
            raise FileNotFoundError(f"pasta da instância não encontrada: {src_dir}")

        self._backup_conf()
        # nova porta ADB = maior existente + 1
        used = [p for p in (self.adb_port(n) for n in self.list_instances()) if p]
        new_port = (max(used) if used else 5555) + 1

        text = self.conf_path.read_text(encoding="utf-8", errors="replace")
        prefix = f"bst.instance.{source}."
        for key, val in conf.items():
            if key.startswith(prefix):
                new_key = f"bst.instance.{dest}." + key[len(prefix):]
                if new_key.endswith(".adb_port") or new_key.endswith(".status.adb_port"):
                    val = str(new_port)
                elif new_key.endswith(".display_name"):
                    val = f"{val} ({dest})"
                text = set_conf_line(text, new_key, val)
        names = instance_names_from_conf(conf) + [dest]
        text = set_conf_line(text, "bst.installed_images", ",".join(names))
        self.conf_path.write_text(text, encoding="utf-8")

        shutil.copytree(src_dir, dst_dir)  # pesado; pode levar minutos
        return f"clonada '{source}' → '{dest}' (adb_port={new_port}). Reinicie o BlueStacks."


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main():
    import argparse
    bs = BlueStacks()
    ap = argparse.ArgumentParser(
        prog="python -m aviator_monitor.device.bluestacks",
        description="Controle do BlueStacks sem cliques (list/ports/start/stop/set-adb/wait/launch/status).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="lista instâncias")
    sub.add_parser("ports", help="mostra {instância: porta ADB}")
    for name in ("start", "stop", "status", "wait"):
        sp = sub.add_parser(name)
        sp.add_argument("instance")
    sp = sub.add_parser("set-adb", help="liga/desliga o ADB global")
    sp.add_argument("state", choices=["on", "off"])
    sp = sub.add_parser("launch", help="abre um app numa instância")
    sp.add_argument("instance")
    sp.add_argument("package")
    args = ap.parse_args()

    if args.cmd == "list":
        for n in bs.list_instances():
            print(f"  {n}  ->  {bs.adb_serial(n)}  (rodando={bs.is_running(n)})")
    elif args.cmd == "ports":
        for n, p in bs.ports().items():
            print(f"  {n}: {p}")
    elif args.cmd == "start":
        bs.start(args.instance)
        print(f"subindo '{args.instance}'… use `wait {args.instance}` p/ aguardar o boot.")
    elif args.cmd == "stop":
        print("parada." if bs.stop(args.instance) else "não estava rodando.")
    elif args.cmd == "set-adb":
        bak = bs.set_adb(args.state == "on")
        print(f"ADB {'ligado' if args.state == 'on' else 'desligado'}. Backup da conf: {bak}")
        print("Reinicie a instância p/ valer.")
    elif args.cmd == "wait":
        print(f"pronto: {bs.wait_ready(args.instance)}")
    elif args.cmd == "launch":
        bs.launch_app(args.instance, args.package)
        print(f"abrindo {args.package} em '{args.instance}'…")
    elif args.cmd == "status":
        for k, v in bs.status(args.instance).items():
            print(f"  {k:14s}: {v}")


if __name__ == "__main__":
    main()
