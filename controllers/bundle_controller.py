from flask import Blueprint, jsonify, request
from services.storage_service import StorageService
from pathlib import Path
from services.gerar_hash import gerar_hash
import time
import logging
from repository.bundle_repository import BundleRepository 

bundle_bp = Blueprint("bundle", __name__)

# Configura logger
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Caminhos principais
BASE_PATH = Path(__file__).resolve().parent.parent
MEDIA_PATH = BASE_PATH / "media_data"

# Serviço de arquivos da pasta media_data
storage_service = StorageService(media_path=MEDIA_PATH)

def is_hashed(name: str) -> bool:
    """
    Retorna True se o stem do arquivo contiver um hífen, indicando que já foi hasheado.
    """
    stem = Path(name).stem
    return '-' in stem

def list_filtered_files() -> list[str]:
    """
    Retorna todos os arquivos em media_data, exceto:
      - Arquivos parciais (*.part)
      - Diretórios
    """
    all_names = storage_service.list_files()
    return [name for name in all_names if not name.endswith(".part")]

@bundle_bp.route("/bundle", defaults={"hash_secondary": None}, methods=["GET"])
@bundle_bp.route("/bundle/<hash_secondary>", methods=["GET"])
def get_bundle(hash_secondary):
    # logger.info("/bundle called (secondary hash=%s)", hash_secondary)
    # Aguarda até que todos os arquivos estejam renomeados pelo watcher
    while True:
        files_now = list_filtered_files()
        # logger.info("Arquivos encontrados: %s", files_now)
        un_hashed = [f for f in files_now if not is_hashed(f)]
        if not un_hashed:
            # logger.info("Todos os arquivos estão hasheados (contêm '-').")
            break
        # logger.info("Aguardando hasheamento, arquivos sem '-': %s", un_hashed)
        time.sleep(4)

    # Re-lista arquivos já processados (sem .part)
    file_names = list_filtered_files()
    # logger.info("Lista final de arquivos: %s", file_names)

    # Monta estrutura inicial do bundle
    bundle = {"bundle": file_names, "status": False}

    # Gera hash principal
    bundle_hash = gerar_hash(bundle)
    bundle["hash"] = bundle_hash
    # logger.info("Bundle hash gerado: %s", bundle_hash)

    # Consulta/inserção no banco
    repo = BundleRepository()
    if hash_secondary:
        result = repo.find_send_by_hash_and_secondary(bundle_hash, hash_secondary)
    else:
        result = repo.find_one_send(bundle_hash)

    if result:
        # logger.info("Bundle existente no banco: %s", result)
        bundle.update({"bundle": result["bundle"], "hash": result["hash"], "status": result["status"]})
    else:
        # logger.info("Inserindo novo bundle no banco: %s", bundle)
        repo.insert_bundle_send(hash_str=bundle_hash, bundle=file_names, status=False, hash_secondary=hash_secondary)

    # logger.info("Respondendo bundle: %s", bundle)
    return jsonify(bundle)
