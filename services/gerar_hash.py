import hashlib
import json
def gerar_hash(bundle_dict: dict) -> str:
    # Ordena os nomes dos arquivos para garantir consistência no hash
    sorted_bundle = {
        **bundle_dict,
        "file_names": sorted(bundle_dict["file_names"])
    }
    bundle_json = json.dumps(sorted_bundle, sort_keys=True)
    return hashlib.sha256(bundle_json.encode()).hexdigest()