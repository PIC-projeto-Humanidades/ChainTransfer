# download_file client

from pathlib import Path
import requests
import logging
from colorama import init, Fore, Style
import shutil

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

    # Retoma se já existe parcial
    downloaded_bytes = tmp_path.stat().st_size if tmp_path.exists() else 0
    headers = {"Range": f"bytes={downloaded_bytes}-"} if downloaded_bytes else {}

    try:
        logger.info(f"🚀 Iniciando download de {file_name} de {ip}")
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
        logger.info(f"📥 {file_name}: retomando em {downloaded_bytes} bytes de {total_expected or 'desconhecido'}")

        current_size = downloaded_bytes
        with tmp_path.open(mode) as f:
            for chunk in res.iter_content(chunk_size=1024*1024):
                if not chunk:
                    continue
                f.write(chunk)
                current_size += len(chunk)
                if total_expected:
                    pct = (current_size / total_expected) * 100
                    logger.info(f"⏳ {file_name}: {pct:.2f}% ({current_size}/{total_expected} bytes)")
                else:
                    logger.info(f"⏳ {file_name}: {current_size} bytes baixados")

        # Verifica conclusão
        final_size = tmp_path.stat().st_size
        if total_expected and final_size < total_expected:
            logger.error(f"❌ {file_name} incompleto: {final_size}/{total_expected} bytes")
            return False
        if not total_expected and final_size == 0:
            logger.error(f"❌ {file_name} falhou sem baixar nenhum byte")
            return False

        # Move para media_data
        shutil.move(str(tmp_path), str(final_path))
        logger.info(f"✅ Download completo: {file_name}")
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"⚠️ Erro de conexão ao baixar {file_name}: {e}")
        return False
    except Exception as e:
        logger.error(f"⚠️ Erro inesperado ao processar {file_name}: {e}")
        return False
