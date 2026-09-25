"""Coleta a lista de vídeos de canais do YouTube (sem baixar vídeo) e grava um CSV por canal.

Uso:
    pip install yt-dlp
    python coletar.py                 # canais padrão abaixo
    python coletar.py @3blue1brown    # um canal específico

O modo "flat" (lista da aba Vídeos) traz título, duração e views arredondadas; é rápido e
raramente bloqueia. O modo completo (--completo) abre cada vídeo e traz data, descrição,
likes, capítulos e faixas de dublagem — mas a partir de IP de nuvem o YouTube costuma pedir
login ("confirme que não é robô"). Rodando no PC de casa funciona; se não, passe
--cookies-from-browser chrome para o yt-dlp.
"""
import csv
import json
import subprocess
import sys
from pathlib import Path

CANAIS_PADRAO = [
    "@3blue1brown",
    "@OverSimplified",
    "@SamONellaAcademy",
    "@kurzgesagt",
    "@CienciaTodoDia",
    "@nerdologia",
    "@BuenasIdeias",
    "@ManualdoMundo",
]

PASTA_DADOS = Path(__file__).parent / "dados"


def listar_videos(canal, aba="videos"):
    """Lista rápida (flat) dos vídeos de uma aba do canal."""
    saida = subprocess.run(
        ["yt-dlp", "--flat-playlist", "-J", f"https://www.youtube.com/{canal}/{aba}"],
        capture_output=True, text=True, check=True,
    )
    dados = json.loads(saida.stdout)
    return dados, dados.get("entries", [])


def detalhar_videos(canal):
    """Metadados completos de cada vídeo (lento; pode ser bloqueado em IP de nuvem)."""
    saida = subprocess.run(
        ["yt-dlp", "--skip-download", "-j", "--no-warnings", "--ignore-errors",
         f"https://www.youtube.com/{canal}/videos"],
        capture_output=True, text=True,
    )
    return [json.loads(linha) for linha in saida.stdout.splitlines() if linha.strip()]


def gravar_csv(canal, dados, videos):
    PASTA_DADOS.mkdir(exist_ok=True)
    arquivo = PASTA_DADOS / f"{canal.lstrip('@').lower()}.csv"
    with open(arquivo, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ordem_mais_novo_primeiro", "id", "titulo", "duracao_min", "views"])
        for i, v in enumerate(videos):
            duracao = round(v["duration"] / 60, 1) if v.get("duration") else ""
            w.writerow([i, v["id"], v["title"], duracao, v.get("view_count") or ""])
    print(f"{dados.get('channel')}: {len(videos)} vídeos, "
          f"{dados.get('channel_follower_count')} inscritos -> {arquivo.name}")


if __name__ == "__main__":
    argumentos = [a for a in sys.argv[1:] if not a.startswith("--")]
    for canal in argumentos or CANAIS_PADRAO:
        dados, videos = listar_videos(canal)
        gravar_csv(canal, dados, videos)
        if "--completo" in sys.argv:
            completos = detalhar_videos(canal)
            destino = PASTA_DADOS / f"{canal.lstrip('@').lower()}-completo.jsonl"
            with open(destino, "w", encoding="utf-8") as f:
                for v in completos:
                    v.pop("formats", None)
                    f.write(json.dumps(v, ensure_ascii=False) + "\n")
            print(f"   completo: {len(completos)} vídeos -> {destino.name}")
