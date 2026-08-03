"""Monitor de Aviator — captura de multiplicadores em tempo real.

Pipeline: captura (frames) -> whacamolefinder (gatilho) -> OCR (Tesseract)
-> dedup -> SQLite -> análise/observabilidade (CLI + Streamlit).

Nota honesta: o Aviator é provably-fair; o histórico NÃO prevê o próximo número.
O valor é o pipeline de visão computacional e o estudo da distribuição. Ver SPEC-02.
"""
__version__ = "0.1.0"
