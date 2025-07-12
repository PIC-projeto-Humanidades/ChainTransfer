# services/gerar_hash.py

import hashlib
import json

def gerar_hash(bundle_dict: dict) -> str:
    """
    Gera um hash SHA256 único a partir da lista de arquivos.
    Aceita chaves 'file_names' ou 'bundle'.
    """
    # Suporta ambos os formatos
    file_list = bundle_dict.get("file_names")
    if file_list is None:
        file_list = bundle_dict.get("bundle", [])

    # Garante lista ordenada
    sorted_files = sorted(file_list)

    # Serializa apenas os nomes de arquivo para o hash
    data = json.dumps({"file_names": sorted_files}, separators=(",", ":"), ensure_ascii=False)
    # Calcula SHA256 e retorna hex digest
    return hashlib.sha256(data.encode("utf-8")).hexdigest()
