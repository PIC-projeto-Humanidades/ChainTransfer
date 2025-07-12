from pathlib import Path
import os
import time
import requests
import threading
import json
import uuid

# Importa serviços e repositórios do sistema
from services.network_service import routes,meu_ip           # Lista de nós conhecidos da rede, meu ip
from utils.ping import ping                                  # Função para verificar se um IP está ativo
from utils.hash_do_ip import hash_do_ip                      # Função para hashear o IP está ativo
from services.storage_service import StorageService          # Serviço para manipular arquivos locais
from services.download_file import download_file             # Função para fazer o download de arquivos
from repository.bundle_repository import BundleRepository    # Repositório para manipular bundles recebidos
from repository.files_receiver_repository import FilesReceiverRepository  # Repositório de arquivos baixados

# Caminho para a pasta onde os arquivos locais serão monitorados
MEDIA_PATH = Path(os.getcwd()) / "media_data"

# Caminho para a pasta onde os arquivos recebidos serão armazenados
RECEIVER_PATH = Path(__file__).resolve().parent.parent / "receiver"

# Verifica se um texto é um UUID válido (para identificação de arquivos)
def is_valid_uuid(text):
    try:
        uuid.UUID(text)
        return True
    except ValueError:
        return False

# 🧠 Thread 1: Observa a pasta `media_data` e renomeia arquivos automaticamente com UUID
def observe_and_rename():
    print("👁️ Observando a pasta media_data para novos arquivos...")
    MEDIA_PATH.mkdir(parents=True, exist_ok=True)

    # Mantém uma lista de arquivos já vistos
    seen = set(f.name for f in MEDIA_PATH.iterdir() if f.is_file())

    while True:
        time.sleep(5)  # Checa a cada 5 segundos
        for file in MEDIA_PATH.iterdir():
            if file.is_file() and file.name not in seen:
                seen.add(file.name)

                # Se o arquivo não contém um UUID no nome, renomeia com um novo
                if '-' not in file.stem or not is_valid_uuid(file.stem.split('-')[-1]):
                    new_name = f"{file.stem}-{uuid.uuid4()}{file.suffix}"
                    new_path = MEDIA_PATH / new_name
                    file.rename(new_path)
                    seen.remove(file.name)
                    seen.add(new_name)
                    print(f"📝 Arquivo renomeado: {file.name} → {new_name}")

# 🔁 Thread 2: Rotina que busca bundles nos nós da rede e faz o download dos arquivos
def routine():
    storage_service = StorageService(media_path=RECEIVER_PATH)
    instance_BundleRepository = BundleRepository()
    instance_FilesReceiverRepository = FilesReceiverRepository()
    print("⏳ Iniciando rotina recorrente a cada 5 segundos...")

    while True:
        time.sleep(5)
        print("🔍 Procurando bundles em nós ativos...")

        for node in routes():
            ip = node["ip"]

            # Verifica se o nó está ativo via ping
            if not ping(ip):
                continue

            print(f"📡 Dispositivo ativo - IP: {ip}, Node: {node['node']}")
            try:
                meu_ip_network = meu_ip()
                hash_secondary = hash_do_ip(meu_ip_network)
                # Solicita o bundle ao nó remoto
                res = requests.get(f"http://{ip}:3000/bundle/{hash_secondary}", timeout=5)
                bundle = res.json()
                bundle_hash = bundle.get("hash")
                files = bundle.get("bundle", [])

                # Verifica se o bundle recebido é válido
                if not bundle_hash or not isinstance(files, list):
                    print("⚠️ Bundle inválido recebido, ignorando.")
                    continue

                # Verifica se já temos esse bundle no banco
                resultSearch = instance_BundleRepository.find_one_receiver(bundle_hash)
                if resultSearch:
                    if resultSearch["status"]:
                        print(f"✅ Bundle {bundle_hash} já concluído.")
                        continue  # Nada a fazer
                    else:
                        print(f"ℹ️ Bundle {bundle_hash} ainda não concluído.")
                        bundleDatabase = resultSearch
                else:
                    # Novo bundle, insere no banco como não concluído
                    print(f"📦 Novo bundle recebido: {bundle_hash}")
                    instance_BundleRepository.insert_bundle_receiver(bundle_hash, files, False)
                    bundleDatabase = {
                        "hash": bundle_hash,
                        "bundle": files,
                        "status": False
                    }

                # Filtra apenas os arquivos ainda não baixados
                listaFiltrada_arquivos = []
                for file_name in bundleDatabase["bundle"]:
                    resultado = instance_FilesReceiverRepository.find_by_file_name(file_name)
                    if not resultado:
                        listaFiltrada_arquivos.append(file_name)

                # Faz o download dos arquivos pendentes
                for file_name in listaFiltrada_arquivos:
                    resultDownload = download_file(ip, file_name)
                    if resultDownload:
                        instance_FilesReceiverRepository.insert_file(bundle_hash, file_name)
                        print(f"📥 Download do arquivo {file_name} feito com sucesso.")
                    else:
                        print(f"❌ Falha ao realizar o download do arquivo {file_name}.")

                # Verifica se todos os arquivos foram baixados
                finally_files = instance_FilesReceiverRepository.find_by_hash(bundle_hash)
                arquivos_esperados = bundleDatabase["bundle"]
                arquivos_baixados = [row["file_name"] for row in finally_files]
                todos_baixados = all(nome in arquivos_baixados for nome in arquivos_esperados)

                # Atualiza status se tudo estiver completo
                if todos_baixados:
                    print(f"✅ Todos os arquivos do bundle {bundle_hash} foram baixados.")
                    instance_BundleRepository.update_status_receiver(bundle_hash, True)
                else:
                    faltando = [nome for nome in arquivos_esperados if nome not in arquivos_baixados]
                    print(f"⚠️ Ainda faltam arquivos para o bundle {bundle_hash}: {faltando}")

            except Exception as e:
                print(f"❌ Erro ao processar o nó {ip}: {e}")

# 🔁 Inicia duas threads paralelas:
# - Uma para observar novos arquivos locais
# - Outra para buscar e baixar arquivos de outros nós
threading.Thread(target=observe_and_rename, daemon=True).start()
threading.Thread(target=routine, daemon=True).start()
