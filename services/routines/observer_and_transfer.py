# services/routines/observer_and_transfer.py

import os
import time
import uuid
import requests
import logging
from pathlib import Path
from colorama import init, Fore, Style

from services.network_service import meu_ip, routes
from utils.ping import ping
from utils.hash_do_ip import hash_do_ip
from services.download_file import download_file
from repository.bundle_repository import BundleRepository
from repository.files_receiver_repository import FilesReceiverRepository

# Inicializa Colorama
init(autoreset=True)

# Configura logger com cores
class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED + Style.BRIGHT,
    }
    def format(self, record):
        msg = super().format(record)
        color = self.COLORS.get(record.levelno, "")
        return f"{color}{msg}{Style.RESET_ALL}"

logger = logging.getLogger("observer_and_transfer")
handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

MEDIA_PATH = Path(os.getcwd()) / "media_data"

def is_valid_uuid(text: str) -> bool:
    try:
        uuid.UUID(text)
        return True
    except ValueError:
        return False

def observe_and_rename():
    logger.info("👁️  Observando a pasta media_data para novos arquivos...")
    MEDIA_PATH.mkdir(parents=True, exist_ok=True)
    processed = set()

    while True:
        for file in MEDIA_PATH.iterdir():
            if not file.is_file() or file.name in processed:
                continue
            processed.add(file.name)

            stem = file.stem
            # pula stems muito longos
            if len(stem) > 50:
                logger.warning(f"Stem muito longo, pulando: {stem}")
                continue

            parts = stem.rsplit('-', 1)
            if len(parts) == 2 and is_valid_uuid(parts[1]):
                continue

            new_name = f"{stem}-{uuid.uuid4()}{file.suffix}"
            new_path = MEDIA_PATH / new_name
            try:
                file.rename(new_path)
                logger.info(f"📝 Arquivo renomeado: {file.name} → {new_name}")
                processed.add(new_name)
            except OSError as e:
                logger.error(f"❌ Falha ao renomear {file.name}: {e}")

        time.sleep(5)

def routine():
    bundle_repo = BundleRepository()
    files_repo = FilesReceiverRepository()
    logger.info("⏳ Iniciando rotina recorrente a cada 10 segundos...")

    bundle_status_cache = {}

    while True:
        time.sleep(10)
        logger.info("🔍 Procurando bundles em nós ativos...")

        seen_ips = set()
        unique_nodes = []
        for node in routes():
            ip = node["ip"]
            if ip not in seen_ips:
                seen_ips.add(ip)
                unique_nodes.append(node)

        for node in unique_nodes:
            ip = node["ip"]
            if not ping(ip):
                continue

            try:
                my_ip = meu_ip()
                secondary_hash = hash_do_ip(my_ip)
                logger.info("⏳ Obtendo bundles em nós ativos...")
                res = requests.get(f"http://{ip}:3000/bundle/{secondary_hash}", timeout=(5, 65))
                logger.info("✅ Bundle em nós ativos recebido com sucesso")
                try:
                    bundle = res.json()
                except ValueError:
                    logger.warning(f"❌ Resposta inválida de {ip}: {res.text[:100]}...")
                    continue

                bundle_hash = bundle.get("hash")
                files = bundle.get("bundle", [])
                if not bundle_hash or not isinstance(files, list):
                    logger.warning(f"⚠️ Bundle inválido de {ip}, ignorando.")
                    continue

                prev_status = bundle_status_cache.get(bundle_hash)
                record = bundle_repo.find_one_receiver(bundle_hash)
                current_status = bool(record and record.get("status"))

                if record is None:
                    logger.info(f"📦 Novo bundle recebido: {bundle_hash}")
                    bundle_repo.insert_bundle_receiver(bundle_hash, files, False)
                    current_status = False

                if current_status and prev_status is not True:
                    logger.info(f"✅ Bundle {bundle_hash} concluído.")

                bundle_status_cache[bundle_hash] = current_status

                if current_status:
                    continue

                # coleta só os arquivos que ainda não estão no DB
                initial_to_download = [f for f in files if not files_repo.find_by_file_name(f)]

                # verifica se algum desse initial_to_download já existe em media_data
                existing = {f.name for f in MEDIA_PATH.iterdir() if f.is_file()}
                to_download = []
                for fname in initial_to_download:
                    if fname in existing:
                        # registra como já baixado
                        files_repo.insert_file(bundle_hash, fname)
                        logger.info(f"ℹ️ Arquivo já existente em media_data: {fname} — marcando como recebido")
                    else:
                        to_download.append(fname)

                # agora baixa de fato só o que falta
                for fname in to_download:
                    ok = download_file(ip, fname)
                    if ok:
                        files_repo.insert_file(bundle_hash, fname)

                downloaded = {r.get("file_name") for r in files_repo.find_by_hash(bundle_hash)}
                if set(files) <= downloaded:
                    bundle_repo.update_status_receiver(bundle_hash, True)
                    bundle_status_cache[bundle_hash] = True
                    logger.info(f"✅ Todos os arquivos do bundle {bundle_hash} foram baixados.")

            except Exception as e:
                logger.error(f"❌ Erro ao processar o nó {ip}: {e}")
