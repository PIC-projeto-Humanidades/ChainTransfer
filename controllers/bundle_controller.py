from flask import Blueprint, jsonify, request
from services.storage_service import StorageService
from pathlib import Path
from services.gerar_hash import gerar_hash

bundle_bp = Blueprint("bundle", __name__)
storage_service = StorageService(media_path=Path(__file__).resolve().parent.parent / "media_data")

@bundle_bp.route("/bundle", methods=["GET"])
def get_bundle():
    source_node = request.args.get("source_node", "undefined")
    destination_node = request.args.get("destination_node", "undefined")
    session = request.args.get("session", "sessao-generica")

    file_names = storage_service.list_files()
    bundle = {
        "bundle": f"{source_node}-{destination_node}-{session}",
        "file_names": file_names,
        "source_node": source_node,
        "destination_node": destination_node,
        "session": session
    }
    bundle["hash"] = gerar_hash(bundle)
    return jsonify(bundle)
