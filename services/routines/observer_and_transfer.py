# app.py ou routines.py

from pathlib import Path
import os
import time
import requests
import threading
import json
import uuid

from services.network_service import routes
from utils.ping import ping
from services.storage_service import StorageService
from services.download_file import download_file

MEDIA_PATH = Path(os.getcwd()) / "media_data"
RECEIVER_PATH =  Path(__file__).resolve().parent.parent / "receiver"
BUNDLES_LOG = Path(__file__).resolve().parent.parent / "logs" / "bundles_log.json"

def load_bundles_log():
    if not BUNDLES_LOG.exists():
        return {}
    with open(BUNDLES_LOG, "r") as f:
        return json.load(f)

def save_bundles_log(data):
    with open(BUNDLES_LOG, "w") as f:
        json.dump(data, f, indent=2)

def is_valid_uuid(text):
    try:
        uuid.UUID(text)
        return True
    except ValueError:
        return False

def observe_and_rename():
    print("👁️ Observando a pasta media_data para novos arquivos...")
    MEDIA_PATH.mkdir(parents=True, exist_ok=True)
    seen = set(f.name for f in MEDIA_PATH.iterdir() if f.is_file())

    while True:
        time.sleep(1)
        for file in MEDIA_PATH.iterdir():
            if file.is_file() and file.name not in seen:
                seen.add(file.name)
                if '-' not in file.stem or not is_valid_uuid(file.stem.split('-')[-1]):
                    new_name = f"{file.stem}-{uuid.uuid4()}{file.suffix}"
                    new_path = MEDIA_PATH / new_name
                    file.rename(new_path)
                    seen.remove(file.name)
                    seen.add(new_name)
                    print(f"📝 Arquivo renomeado: {file.name} → {new_name}")

def routine():
    storage_service = StorageService(media_path=RECEIVER_PATH)
    print("⏳ Iniciando rotina recorrente a cada 2 segundos...")

    while True:
        time.sleep(5)
        print("Procurando ...")
        for node in routes():
            ip = node["ip"]
            if not ping(ip):
                # print(f"❌ {ip} inativo.")
                continue

            print(f"📡 Dispositivo ativo - IP: {ip}, Node: {node['node']}")
            try:
                res = requests.get(f"http://{ip}:3000/bundle", timeout=5)
                bundle = res.json()
                bundle_hash = bundle.get("hash")
                files = bundle.get("file_names", [])
                session = bundle.get("session")
                source_node = bundle.get("source_node")
                bundle_id = f"{bundle_hash}"

                bundles_log = load_bundles_log()
                if bundle_id in bundles_log and bundles_log[bundle_id].get("status") == "concluido":
                    print(f"✅ Bundle {bundle_id} já concluído.")
                    continue

                if bundle_id not in bundles_log:
                    bundles_log[bundle_id] = {
                        "session": session,
                        "source_node": source_node,
                        "arquivos": {},
                        "status": "incompleto"
                    }

                for file in files:
                    if bundles_log[bundle_id]["arquivos"].get(file) == "ok":
                        continue

                    success = download_file(ip, file, session, source_node)
                    if success:
                        bundles_log[bundle_id]["arquivos"][file] = "ok"
                        print(f"📥 {file} baixado.")
                    else:
                        print(f"⚠️ Erro em {file}. Re-tentando...")
                        retry = download_file(ip, file, session, source_node)
                        if retry:
                            bundles_log[bundle_id]["arquivos"][file] = "ok"
                            print(f"✅ {file} baixado na segunda tentativa.")
                        else:
                            print(f"❌ Falha em definitivo: {file}.")

                if all(bundles_log[bundle_id]["arquivos"].get(f) == "ok" for f in files):
                    bundles_log[bundle_id]["status"] = "concluido"
                    print(f"🎉 Bundle {bundle_id} completo.")

                    try:
                        feedback = {
                            "hash": bundle_hash,
                            "session": session,
                            "destination_node": node["node"],
                            "status": "ok"
                        }
                        fb_res = requests.post(f"http://{ip}:3000/monitoring/feedback", json=feedback, timeout=5)
                        if fb_res.status_code in [200, 201]:
                            print("📬 Feedback enviado.")
                    except Exception as e:
                        print(f"⚠️ Erro no feedback: {e}")

                save_bundles_log(bundles_log)

            except Exception as e:
                print(f"❌ Erro ao conectar ao {ip}: {e}")

# Inicia observadores
threading.Thread(target=observe_and_rename, daemon=True).start()
threading.Thread(target=routine, daemon=True).start()
