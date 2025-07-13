from pathlib import Path
import os
import time
import requests
import threading
import json
import uuid

from services.network_service import meu_ip, routes
from utils.ping import ping
from utils.hash_do_ip import hash_do_ip
from services.download_file import download_file
from repository.bundle_repository import BundleRepository
from repository.files_receiver_repository import FilesReceiverRepository

MEDIA_PATH = Path(os.getcwd()) / "media_data"
RECEIVER_PATH = Path(__file__).resolve().parent.parent / "receiver"

def is_valid_uuid(text):
    try:
        uuid.UUID(text)
        return True
    except ValueError:
        return False

def observe_and_rename():
    print("👁️ Observando a pasta media_data para novos arquivos...")
    MEDIA_PATH.mkdir(parents=True, exist_ok=True)
    seen = set()

    while True:
        for file in MEDIA_PATH.iterdir():
            if not file.is_file() or file.name in seen:
                continue
            seen.add(file.name)

            stem = file.stem
            last = stem.split("-")[-1]
            if "-" not in stem or not is_valid_uuid(last):
                new_name = f"{stem}-{uuid.uuid4()}{file.suffix}"
                new_path = MEDIA_PATH / new_name
                file.rename(new_path)
                print(f"📝 Arquivo renomeado: {file.name} → {new_name}")
                seen.add(new_name)

        time.sleep(5)


def routine():
    instance_BundleRepository = BundleRepository()
    instance_FilesReceiverRepository = FilesReceiverRepository()
    print("⏳ Iniciando rotina recorrente a cada 5 segundos...")

    while True:
        time.sleep(5)
        print("🔍 Procurando bundles em nós ativos...")

        # Elimina duplicatas por IP para não logar várias vezes
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

            print(f"📡 Dispositivo ativo - IP: {ip}, Node: {node['node']}")
            try:
                meu_ip_network = meu_ip(routes())
                hash_secondary = hash_do_ip(meu_ip_network)
                res = requests.get(f"http://{ip}:3000/bundle/{hash_secondary}", timeout=5)
                try:
                    bundle = res.json()
                except ValueError:
                    print(f"❌ Resposta inválida do {ip}: {res.text}")
                    continue

                bundle_hash = bundle.get("hash")
                files = bundle.get("bundle", [])
                if not bundle_hash or not isinstance(files, list):
                    print("⚠️ Bundle inválido recebido, ignorando.")
                    continue

                result = instance_BundleRepository.find_one_receiver(bundle_hash)
                if result and result["status"]:
                    print(f"✅ Bundle {bundle_hash} já concluído.")
                    continue

                if not result:
                    print(f"📦 Novo bundle recebido: {bundle_hash}")
                    instance_BundleRepository.insert_bundle_receiver(bundle_hash, files, False)
                    bundle_db = {"hash": bundle_hash, "bundle": files, "status": False}
                else:
                    print(f"ℹ️ Bundle {bundle_hash} ainda não concluído.")
                    bundle_db = result

                to_download = [
                    f for f in bundle_db["bundle"]
                    if not instance_FilesReceiverRepository.find_by_file_name(f)
                ]

                for fname in to_download:
                    ok = download_file(ip, fname)
                    if ok:
                        instance_FilesReceiverRepository.insert_file(bundle_hash, fname)
                        print(f"📥 Download do arquivo {fname} feito com sucesso.")
                    else:
                        print(f"❌ Falha ao baixar {fname}.")

                all_files = instance_FilesReceiverRepository.find_by_hash(bundle_hash)
                downloaded = {r["file_name"] for r in all_files}
                expected = set(bundle_db["bundle"])
                if expected <= downloaded:
                    print(f"✅ Todos os arquivos do bundle {bundle_hash} foram baixados.")
                    instance_BundleRepository.update_status_receiver(bundle_hash, True)
                else:
                    missing = list(expected - downloaded)
                    print(f"⚠️ Faltam arquivos para o bundle {bundle_hash}: {missing}")

            except Exception as e:
                print(f"❌ Erro ao processar o nó {ip}: {e}")
