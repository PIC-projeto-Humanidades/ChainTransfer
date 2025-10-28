# download_file client

from pathlib import Path
import requests
import logging
import shutil
from logs.log_f import log_f as logger 
from services.metrics_service import log_envio
from time import time

# Pastas de trabalho
BASE_DIR       = Path(__file__).resolve().parent.parent
PROCESS_DIR    = BASE_DIR / "download_processamento"
MEDIA_DIR      = BASE_DIR / "media_data"
PROCESS_DIR.mkdir(parents=True, exist_ok=True)
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

def download_file(ip, file_name):
    url = f"http://{ip}:3000/file/{file_name}"
    tmp_path   = PROCESS_DIR / (file_name + ".part")
    final_path = MEDIA_DIR / file_name
    tmp_path.parent.mkdir(parents=True, exist_ok=True)

    downloaded_bytes = tmp_path.stat().st_size if tmp_path.exists() else 0
    headers = {"Range": f"bytes={downloaded_bytes}-"} if downloaded_bytes else {}

    tentativa = 1
    resultado = "falha"
    motivo_falha = ""
    t_inicio = time()
    t_fim = None
    tamanho_bytes = 0
    try:
        logger(f"🚀 Iniciando download de {file_name} de {ip}")
        res = requests.get(url, headers=headers, stream=True, timeout=30)
        if res.status_code not in (200, 206):
            logger(f"Falha ao baixar {file_name} — Status {res.status_code}")
            motivo_falha = f"HTTP {res.status_code}"
            t_fim = time()
            log_envio(
                arquivo=file_name,
                tamanho_bytes=downloaded_bytes,
                destino=ip,
                tentativa=tentativa,
                resultado=resultado,
                motivo_falha=motivo_falha,
                timestamp_inicio=str(t_inicio),
                timestamp_fim=str(t_fim)
            )
            return False
        if "Content-Range" in res.headers:
            total_expected = int(res.headers["Content-Range"].split("/")[-1])
        else:
            total_expected = int(res.headers.get("Content-Length", 0))
        mode = "ab" if downloaded_bytes else "wb"
        logger(f"📥 {file_name}: retomando em {downloaded_bytes} bytes de {total_expected or 'desconhecido'}")
        current_size = downloaded_bytes
        with tmp_path.open(mode) as f:
            for chunk in res.iter_content(chunk_size=1024*1024):
                if not chunk:
                    continue
                f.write(chunk)
                current_size += len(chunk)
                if total_expected:
                    pct = (current_size / total_expected) * 100
                    logger(f"⏳ {file_name}: {pct:.2f}% ({current_size}/{total_expected} bytes)")
                else:
                    logger(f"⏳ {file_name}: {current_size} bytes baixados")
        final_size = tmp_path.stat().st_size
        if total_expected and final_size < total_expected:
            logger(f"❌ {file_name} incompleto: {final_size}/{total_expected} bytes")
            motivo_falha = "incompleto"
            t_fim = time()
            log_envio(
                arquivo=file_name,
                tamanho_bytes=final_size,
                destino=ip,
                tentativa=tentativa,
                resultado=resultado,
                motivo_falha=motivo_falha,
                timestamp_inicio=str(t_inicio),
                timestamp_fim=str(t_fim)
            )
            return False
        if not total_expected and final_size == 0:
            logger(f"❌ {file_name} falhou sem baixar nenhum byte")
            motivo_falha = "sem bytes"
            t_fim = time()
            log_envio(
                arquivo=file_name,
                tamanho_bytes=final_size,
                destino=ip,
                tentativa=tentativa,
                resultado=resultado,
                motivo_falha=motivo_falha,
                timestamp_inicio=str(t_inicio),
                timestamp_fim=str(t_fim)
            )
            return False
        shutil.move(str(tmp_path), str(final_path))
        logger(f"✅ Download completo: {file_name}")
        resultado = "sucesso"
        t_fim = time()
        log_envio(
            arquivo=file_name,
            tamanho_bytes=final_size,
            destino=ip,
            tentativa=tentativa,
            resultado=resultado,
            motivo_falha=motivo_falha,
            timestamp_inicio=str(t_inicio),
            timestamp_fim=str(t_fim)
        )
        return True
    except requests.exceptions.RequestException as e:
        logger(f"⚠️ Erro de conexão ao baixar {file_name}: {e}")
        motivo_falha = str(e)
        t_fim = time()
        log_envio(
            arquivo=file_name,
            tamanho_bytes=downloaded_bytes,
            destino=ip,
            tentativa=tentativa,
            resultado=resultado,
            motivo_falha=motivo_falha,
            timestamp_inicio=str(t_inicio),
            timestamp_fim=str(t_fim)
        )
        return False
    except Exception as e:
        logger(f"⚠️ Erro inesperado ao processar {file_name}: {e}")
        motivo_falha = str(e)
        t_fim = time()
        log_envio(
            arquivo=file_name,
            tamanho_bytes=downloaded_bytes,
            destino=ip,
            tentativa=tentativa,
            resultado=resultado,
            motivo_falha=motivo_falha,
            timestamp_inicio=str(t_inicio),
            timestamp_fim=str(t_fim)
        )
        return False
