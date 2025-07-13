from flask import Blueprint, jsonify, request
from services.storage_service import StorageService
from pathlib import Path
from services.gerar_hash import gerar_hash
import time
import uuid
from repository.bundle_repository import BundleRepository 

bundle_bp = Blueprint("bundle", __name__)

# Caminhos principais
BASE_PATH = Path(__file__).resolve().parent.parent
MEDIA_PATH = BASE_PATH / "media_data"

# Serviço de arquivos da pasta media_data
storage_service = StorageService(media_path=MEDIA_PATH)

def has_uuid_suffix(name: str) -> bool:
    stem = Path(name).stem
    parts = stem.rsplit("-", 1)
    if len(parts) != 2:
        return False
    try:
        uuid.UUID(parts[1])
        return True
    except ValueError:
        return False

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
    # 1) Aguarda indefinidamente até que todos os arquivos estejam hasheados
    while True:
        time.sleep(2)
        files_now = list_filtered_files()
        # encontra quem ainda não recebeu o -UUID
        un_hashed = [f for f in files_now if not has_uuid_suffix(f)]
        if not un_hashed:
            break

    # 2) Re-lista arquivos já processados (sem .part)
    file_names = list_filtered_files()

    # 3) Monta estrutura inicial do bundle
    bundle = {
        "bundle": file_names,
        "status": False
    }

    # 4) Gera hash principal
    bundle_hash = gerar_hash(bundle)
    bundle["hash"] = bundle_hash

    # 5) Consulta/inserção no banco
    repo = BundleRepository()
    if hash_secondary:
        result = repo.find_send_by_hash_and_secondary(bundle_hash, hash_secondary)
    else:
        result = repo.find_one_send(bundle_hash)

    if result:
        bundle["bundle"] = result["bundle"]
        bundle["hash"]   = result["hash"]
        bundle["status"] = result["status"]
    else:
        repo.insert_bundle_send(
            hash_str=bundle_hash,
            bundle=file_names,
            status=False,
            hash_secondary=hash_secondary
        )

    return jsonify(bundle)
