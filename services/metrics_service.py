import os
from pathlib import Path
import csv
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
METRICS_FILE = BASE_DIR / "logs" / "metrics_envio.csv"

HEADER = [
    "timestamp_inicio",
    "timestamp_fim",
    "arquivo",
    "tamanho_bytes",
    "destino",
    "tentativa",
    "resultado",
    "motivo_falha",
    "latencia",
    "taxa_transferencia"
]

def log_envio(
    arquivo,
    tamanho_bytes,
    destino,
    tentativa,
    resultado,
    motivo_falha=None,
    timestamp_inicio=None,
    timestamp_fim=None
):
    if timestamp_inicio is None:
        timestamp_inicio = datetime.now().isoformat()
    if timestamp_fim is None:
        timestamp_fim = datetime.now().isoformat()
    latencia = None
    taxa_transferencia = None
    try:
        t0 = datetime.fromisoformat(timestamp_inicio)
        t1 = datetime.fromisoformat(timestamp_fim)
        latencia = float((t1 - t0).total_seconds())
        if latencia is not None and tamanho_bytes:
            taxa_transferencia = float(tamanho_bytes) / latencia if latencia > 0 else 0.0
    except Exception:
        latencia = 0.0
        taxa_transferencia = 0.0
    # Garante que o diretório logs existe
    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        first_write = not METRICS_FILE.exists()
        with open(METRICS_FILE, "a", newline='') as f:
            writer = csv.writer(f)
            if first_write:
                writer.writerow(HEADER)
            writer.writerow([
                timestamp_inicio,
                timestamp_fim,
                arquivo,
                tamanho_bytes,
                destino,
                tentativa,
                resultado,
                motivo_falha if motivo_falha is not None else "",
                float(latencia) if latencia is not None else 0.0,
                float(taxa_transferencia) if taxa_transferencia is not None else 0.0
            ])
    except Exception as e:
        print(f"[ERRO] Falha ao gravar métricas: {e}")
