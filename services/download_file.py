# download_file client

from pathlib import Path
import requests
import logging
from colorama import init, Fore, Style

# Inicializa Colorama
init(autoreset=True)

class ColorFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }
    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelno, "")
        message = super().format(record)
        return f"{color}{message}{Style.RESET_ALL}"

# Configura logger colorido
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Pasta de destino
RECEIVER_DIR = Path(__file__).resolve().parent.parent / "media_data"
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

        # Obtém tamanho total esperado
        if "Content-Range" in res.headers:
            total_expected = int(res.headers["Content-Range"].split("/")[-1])
        else:
            total_expected = int(res.headers.get("Content-Length", 0))

        mode = "ab" if downloaded_bytes else "wb"
        logger.info(f"Iniciando {file_name}: {downloaded_bytes}/{total_expected or '??'} bytes já baixados")

        current_size = downloaded_bytes
        for chunk in res.iter_content(chunk_size=1024*1024):
            if not chunk:
                continue
            f = tmp_path.open(mode)
            try:
                f.write(chunk)
            finally:
                f.close()
            current_size += len(chunk)
            if total_expected:
                pct = (current_size / total_expected) * 100
                logger.info(f"Progresso: {pct:.2f}% ({current_size}/{total_expected} bytes)")
            else:
                logger.info(f"Progresso: {current_size} bytes")

        # Após o loop, verifica se chegou ao final esperado
        final_size = tmp_path.stat().st_size
        if total_expected:
            if final_size < total_expected:
                logger.error(f"Download incompleto: {final_size}/{total_expected} bytes")
                return False
        else:
            # Se não havia Content-Length, exige ao menos >0 bytes
            if final_size == 0:
                logger.error("Download falhou sem baixar nenhum byte")
                return False

        # Tudo certo: renomeia e retorna True
        tmp_path.rename(final_path)
        logger.info(f"Download completo: {file_name}")
        return True

    except requests.exceptions.RequestException as e:
        # Captura timeouts, conexões interrompidas, etc.
        logger.error(f"Erro de conexão ao baixar {file_name}: {e}")
        return False
    except Exception as e:
        # Qualquer outra falha de IO
        logger.error(f"Erro inesperado ao processar download de {file_name}: {e}")
        return False
