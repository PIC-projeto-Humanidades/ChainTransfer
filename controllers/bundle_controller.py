from flask import Blueprint, jsonify, request
from services.storage_service import StorageService
from pathlib import Path
from services.gerar_hash import gerar_hash
import json
from repository.bundle_repository import BundleRepository 

bundle_bp = Blueprint("bundle", __name__)

# Caminhos principais
BASE_PATH = Path(__file__).resolve().parent.parent
MEDIA_PATH = BASE_PATH / "media_data"

# Serviço de arquivos da pasta media_data
storage_service = StorageService(media_path=MEDIA_PATH)

@bundle_bp.route("/bundle", defaults={"hash_secondary": None}, methods=["GET"])
@bundle_bp.route("/bundle/<hash_secondary>", methods=["GET"])
def get_bundle(hash_secondary):
    # Lista os arquivos atuais
    file_names = storage_service.list_files()

    # Monta estrutura inicial do bundle
    bundle = {
        "bundle": file_names,
        "status": False
    }

    # Gera hash principal com base no conteúdo atual
    bundle_hash = gerar_hash(bundle)
    bundle["hash"] = bundle_hash

    # Tenta encontrar o bundle por hash e hash_secondary, se informado
    instance_BundleRepository = BundleRepository()
    if hash_secondary:
        resultSearch = instance_BundleRepository.find_send_by_hash_and_secondary(bundle_hash, hash_secondary)
    else:
        resultSearch = instance_BundleRepository.find_one_send(bundle_hash)

    if resultSearch:
        # Se já existe, retorna o que está no banco
        bundle["bundle"] = resultSearch["bundle"]
        bundle["hash"] = resultSearch["hash"]
        bundle["status"] = resultSearch["status"]
    else:
        # Se não existe, salva com ou sem hash_secondary
        instance_BundleRepository.insert_bundle_send(
            hash_str=bundle_hash,
            bundle=file_names,
            status=False,
            hash_secondary=hash_secondary
        )

    return jsonify(bundle)
