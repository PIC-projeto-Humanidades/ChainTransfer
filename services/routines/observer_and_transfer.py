# services/routines/observer_and_transfer.py
from pathlib import Path
import os
import time
import requests
import uuid

from services.network_service import meu_ip, routes
from utils.ping import ping
from utils.hash_do_ip import hash_do_ip
from services.download_file import download_file
from repository.bundle_repository import BundleRepository
from repository.files_receiver_repository import FilesReceiverRepository

MEDIA_PATH = Path(os.getcwd()) / "media_data"
RECEIVER_PATH = Path(__file__).resolve().parent.parent / "receiver"


def is_valid_uuid(text: str) -> bool:
    try:
        uuid.UUID(text)
        return True
    except ValueError:
        return False


def observe_and_rename():
    print("👁️ Observando a pasta media_data para novos arquivos...")
    MEDIA_PATH.mkdir(parents=True, exist_ok=True)
    processed = set()

    while True:
        for file in MEDIA_PATH.iterdir():
            if not file.is_file() or file.name in processed:
                continue
            processed.add(file.name)

            stem = file.stem
            if len(stem) > 50:
                continue

            parts = stem.rsplit('-', 1)
            if len(parts) == 2 and is_valid_uuid(parts[1]):
                continue

            new_name = f"{stem}-{uuid.uuid4()}{file.suffix}"
            new_path = MEDIA_PATH / new_name
            try:
                file.rename(new_path)
                print(f"📝 Arquivo renomeado: {file.name} → {new_name}")
                processed.add(new_name)
            except OSError as e:
                print(f"❌ Falha ao renomear {file.name}: {e}")

        time.sleep(5)


def routine():
    bundle_repo = BundleRepository()
    files_repo = FilesReceiverRepository()
    print("⏳ Iniciando rotina recorrente a cada 5 segundos...")

    # Guarda status anterior de cada bundle para evitar logs repetidos
    bundle_status_cache = {}

    while True:
        time.sleep(5)
        print("🔍 Procurando bundles em nós ativos...")

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
                res = requests.get(f"http://{ip}:3000/bundle/{secondary_hash}", timeout=5)

                try:
                    bundle = res.json()
                except ValueError:
                    print(f"❌ Resposta inválida de {ip}: {res.text}")
                    continue

                bundle_hash = bundle.get("hash")
                files = bundle.get("bundle", [])
                if not bundle_hash or not isinstance(files, list):
                    continue

                # Verifica estado antigo
                prev_status = bundle_status_cache.get(bundle_hash)

                record = bundle_repo.find_one_receiver(bundle_hash)
                current_status = bool(record and record.get("status"))

                # Primeiro, loga novo bundle
                if record is None:
                    print(f"📦 Novo bundle recebido: {bundle_hash}")
                    bundle_repo.insert_bundle_receiver(bundle_hash, files, False)
                    current_status = False

                # Se mudou de não concluído para concluído, loga
                if current_status and prev_status is not True:
                    print(f"✅ Bundle {bundle_hash} concluído.")

                # Atualiza cache
                bundle_status_cache[bundle_hash] = current_status

                # Se já concluído antes, pula download
                if current_status:
                    continue

                # Baixa arquivos pendentes
                to_download = [f for f in files if not files_repo.find_by_file_name(f)]
                for fname in to_download:
                    success = download_file(ip, fname)
                    if success:
                        files_repo.insert_file(bundle_hash, fname)
                    # não loga cada arquivo baixado aqui para reduzir flood

                # Atualiza status no repo se todos baixados
                downloaded = {r.get("file_name") for r in files_repo.find_by_hash(bundle_hash)}
                if set(files) <= downloaded:
                    bundle_repo.update_status_receiver(bundle_hash, True)
                    # marco a conclusão para o cache e log
                    bundle_status_cache[bundle_hash] = True
                    print(f"✅ Todos os arquivos do bundle {bundle_hash} foram baixados.")

            except Exception as e:
                print(f"❌ Erro ao processar o nó {ip}: {e}")
