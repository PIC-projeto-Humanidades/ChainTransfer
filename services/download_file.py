# download_file client

from pathlib import Path
import requests
import logging

# Configura logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

RECEIVER_DIR = Path(__file__).resolve().parent.parent / "receiver"
RECEIVER_DIR.mkdir(parents=True, exist_ok=True)


def download_file(ip, file_name):
    url = f"http://{ip}:3000/file/{file_name}"
    tmp_path = RECEIVER_DIR / (file_name + ".part")
    final_path = RECEIVER_DIR / file_name
    tmp_path.parent.mkdir(parents=True, exist_ok=True)

    # Retoma se já existe parcial
    downloaded_bytes = tmp_path.stat().st_size if tmp_path.exists() else 0
    headers = {"Range": f"bytes={downloaded_bytes}-"} if downloaded_bytes else {}

    try:
        res = requests.get(url, headers=headers, stream=True, timeout=30)
        if res.status_code not in (200, 206):
            logger.warning(f"Falha ao baixar {file_name} — Status {res.status_code}")
            return False

        # Determina tamanho total esperado
        if "Content-Range" in res.headers:
            total_expected = int(res.headers["Content-Range"].split("/")[-1])
        else:
            total_expected = int(res.headers.get("Content-Length", 0))

        mode = "ab" if downloaded_bytes else "wb"
        logger.info(f"Iniciando download de {file_name}: {downloaded_bytes}/{total_expected} bytes já baixados")
        with open(tmp_path, mode) as f:
            current_size = downloaded_bytes
            for chunk in res.iter_content(chunk_size=1024*1024):
                if not chunk:
                    continue
                f.write(chunk)
                current_size += len(chunk)
                if total_expected:
                    downloaded_percent = (current_size / total_expected) * 100
                    remaining_percent = 100 - downloaded_percent
                    logger.info(
                        f"Progresso: {current_size}/{total_expected} bytes "
                        f"({downloaded_percent:.2f}% baixado, {remaining_percent:.2f}% restante)"
                    )
                else:
                    logger.info(f"Progresso: {current_size} bytes baixados")

        # Verifica se já recebemos tudo
        current_size = tmp_path.stat().st_size
        if total_expected and current_size < total_expected:
            logger.info(f"Download parcial: {current_size}/{total_expected} bytes salvos em {tmp_path}")
            return False

        tmp_path.rename(final_path)
        logger.info(f"Download completo: {final_path}")
        return True

    except Exception as e:
        logger.error(f"Erro ao baixar {file_name}: {e}")
        return False
